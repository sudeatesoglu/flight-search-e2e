from loguru import logger
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, ElementTimeoutException
from pages.locators import FlightResultPageLocators


class FlightResultPage(BasePage):
    """Page Object for the Enuygun Flight Search Results Page."""

    def wait_for_results_to_load(self) -> None:
        """Wait for the flight results to appear on the screen."""
        logger.info("Waiting for flight result cards to load...")
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located(FlightResultPageLocators.FLIGHT_CARDS)
            )
            logger.info("Flight result cards loaded successfully.")
        except TimeoutException as e:
            logger.error(
                f"TimeoutException: Flight results {FlightResultPageLocators.FLIGHT_CARDS} "
                f"did not load within expected wait time."
            )
            raise ElementTimeoutException("Flight results failed to load.") from e


    def wait_for_flight_list_update(self) -> None:
        """
        Smart wait that handles the React rendering cycle after applying filters.
        Anticipates the loader, then ensures it is completely gone and elements are visible.
        """
        logger.debug("Waiting for flight list update to complete...")
        try:
            WebDriverWait(self.driver, 1.5).until(
                EC.visibility_of_element_located(FlightResultPageLocators.LOADER_SPINNER)
            )
        except TimeoutException:
            pass

        self.wait.until(EC.invisibility_of_element_located(FlightResultPageLocators.LOADER_SPINNER))
        self.wait.until(EC.visibility_of_any_elements_located(FlightResultPageLocators.FLIGHT_CARDS))
        logger.info("Flight list updated and DOM is ready.")


    def apply_departure_time_filter(self, start_time: str, end_time: str) -> None:
        """
        Apply a dynamic departure time filter using ActionChains.
        
        Args:
            start_time (str): Formatted "HH:MM" start time.
            end_time (str): Formatted "HH:MM" end time.
        """
        def time_to_mins(t_str: str) -> int:
            h, m = map(int, t_str.split(':'))
            return h * 60 + m

        target_start_mins = time_to_mins(start_time)
        target_end_mins = time_to_mins(end_time)

        logger.info(f"Applying Departure Time filter: {start_time} - {end_time} ({target_start_mins} - {target_end_mins} mins).")
        logger.info("Opening the accordion panel.")
        
        try:
            self.click_element_with_actions(FlightResultPageLocators.ACCORDION_PANEL)
        except AttributeError:
            # Fallback if the underlying method doesn't exist
            panel = self.find_element(FlightResultPageLocators.ACCORDION_PANEL)
            ActionChains(self.driver).move_to_element(panel).click().perform()
        
        slider_track = self.wait.until(EC.visibility_of_element_located(FlightResultPageLocators.SLIDER_TRACK))
        slider_width = slider_track.size['width']
        max_minutes = 1439.0

        # Left handle (start time)
        left_handle = self.find_element(FlightResultPageLocators.LEFT_HANDLE)
        current_left = int(left_handle.get_attribute("aria-valuenow"))
        
        if current_left < target_start_mins:
            x_offset_left = int(((target_start_mins - current_left) / max_minutes) * slider_width)
            logger.info(f"Human-like dragging left handle to {start_time} (Offset: {x_offset_left}px).")
            
            action = ActionChains(self.driver)
            action.click_and_hold(left_handle).pause(0.5).move_by_offset(x_offset_left, 0).pause(0.5).release().perform()
            
            self.wait_for_flight_list_update()

        # Right handle (end time)
        right_handle = self.find_element(FlightResultPageLocators.RIGHT_HANDLE)
        current_right = int(right_handle.get_attribute("aria-valuenow"))
        
        if current_right > target_end_mins:
            x_offset_right = int(((current_right - target_end_mins) / max_minutes) * slider_width)
            logger.info(f"Human-like dragging right handle to {end_time} (Offset: {-x_offset_right}px).")
            
            action = ActionChains(self.driver)
            action.click_and_hold(right_handle).pause(0.5).move_by_offset(-x_offset_right, 0).pause(0.5).release().perform()
            
            self.wait_for_flight_list_update()


    def get_departure_times(self) -> list[str]:
        """
        Gather all departure times currently displayed in the flight cards.
        
        Returns:
            list[str]: Collection of extracted text representing times.
        """
        logger.info("Retrieving all departure times from displayed flight cards.")
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located(FlightResultPageLocators.DEPARTURE_TIMES))
            
            times = [element.text.strip() for element in elements if element.is_displayed() and element.text.strip()]

            logger.info(f"Retrieved {len(times)} visible departure times.")
            return times
        except TimeoutException as e:
            logger.error("Could not find any departure times on the page.")
            raise ElementTimeoutException("Departure time elements not found.") from e
        

    def apply_airline_filter(self) -> None:
        """
        Open the Airline filter accordion and select Turkish Airlines.
        """
        logger.info("Opening the Airline filter accordion.")
        self.click_element_with_actions(FlightResultPageLocators.AIRLINE_ACCORDION)
        
        logger.info("Waiting for THY checkbox to become visible...")
        self.wait.until(EC.visibility_of_element_located(FlightResultPageLocators.THY_CHECKBOX))

        logger.info("Applying Turkish Airlines (THY) filter.")
        self.click_element_with_actions(FlightResultPageLocators.THY_CHECKBOX)
        
        self.wait_for_flight_list_update()


    def get_displayed_airlines(self) -> list[str]:
        """Extract and return the names of all airlines currently visible on the page."""
        logger.info("Retrieving displayed airline names...")
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located(FlightResultPageLocators.FLIGHT_CARD_AIRLINE_NAME))
            airlines = [el.text.strip() for el in elements if el.is_displayed() and el.text.strip()]
            logger.info(f"Retrieved {len(airlines)} visible airline entries.")
            return airlines
        except TimeoutException:
            logger.warning("No airline names found. Returning empty list.")
            return []
        

    def get_displayed_prices(self) -> list[float]:
        """Extract exact prices using the 'data-price' HTML attribute from visible flight cards."""
        logger.info("Retrieving displayed flight prices using data-price attribute...")
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located(FlightResultPageLocators.FLIGHT_CARD_PRICE))
            
            cleaned_prices = []
            for element in elements:
                if element.is_displayed():
                    price_str = element.get_attribute("data-price")
                    if price_str:
                        cleaned_prices.append(float(price_str))
            
            logger.info(f"Retrieved {len(cleaned_prices)} valid prices.")
            return cleaned_prices
            
        except TimeoutException:
            logger.warning("No price elements found. Returning empty list.")
            return []
        

    def select_first_flight(self, is_return: bool = False, is_final_flight: bool = False) -> None:
        """Click the select button of the first visible flight card and handle package selections and round-trips."""
        logger.info(f"Initiating selection of the first available {'RETURN' if is_return else 'DEPARTURE'} flight.")
        
        btn_locator = FlightResultPageLocators.RETURN_SELECT_BTNS if is_return else FlightResultPageLocators.SELECT_FIRST_FLIGHT_BTN
        
        try:
            buttons = self.wait.until(EC.presence_of_all_elements_located(btn_locator))
            clicked = False
            
            for btn in buttons:
                if btn.is_displayed():
                    self.driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                    logger.info("Clicked 'Seç' button on the targeted visible flight card.")
                    break
            
            if not clicked:
                raise ElementTimeoutException("No visible 'Seç' button found in the target column.")
        except Exception as e:
            logger.error("Failed to find or click the flight select button.")
            raise ElementTimeoutException("Error clicking flight.") from e

        logger.info("Checking if flight package options are displayed...")
        try:

            visible_packages = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_any_elements_located(FlightResultPageLocators.PACKAGE_ITEMS)
            )
            logger.info("Package options appeared. Selecting the first visible package.")
            self.driver.execute_script("arguments[0].click();", visible_packages[0])

            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located(FlightResultPageLocators.PROVIDER_SELECT_BTN)
                )
                logger.info("'Seç ve İlerle' button detected. Clicking it to confirm selection.")
                self.click_element_with_js(FlightResultPageLocators.PROVIDER_SELECT_BTN)
            except TimeoutException:
                pass 

        except TimeoutException:
            logger.info("No package selection appeared. Proceeding to next step.")
            
        if not is_final_flight:
            self.wait_for_flight_list_update()
        else:
            logger.info("Final flight selected. Expecting redirection to the checkout page.")
