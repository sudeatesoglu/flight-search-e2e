import time
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


    def wait_for_loader_to_disappear(self) -> None:
        """Wait for the loader to disappear on the screen."""
        logger.debug("Checking if loader is present and waiting for it to disappear...")
        try:
            self.wait.until(EC.invisibility_of_element_located(FlightResultPageLocators.LOADER_SPINNER))
            logger.info("Loader disappeared, DOM is ready.")
        except TimeoutException:
            logger.warning("Loader did not disappear or took too long. Proceeding anyway...")


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
        
        time.sleep(1)

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
            
            time.sleep(1) 
            self.wait_for_loader_to_disappear()
            time.sleep(1.5)

        # Right handle (end time)
        right_handle = self.find_element(FlightResultPageLocators.RIGHT_HANDLE)
        current_right = int(right_handle.get_attribute("aria-valuenow"))
        
        if current_right > target_end_mins:
            x_offset_right = int(((current_right - target_end_mins) / max_minutes) * slider_width)
            logger.info(f"Human-like dragging right handle to {end_time} (Offset: {-x_offset_right}px).")
            
            action = ActionChains(self.driver)
            action.click_and_hold(right_handle).pause(0.5).move_by_offset(-x_offset_right, 0).pause(0.5).release().perform()
            
            time.sleep(1)
            self.wait_for_loader_to_disappear()
            time.sleep(1.5)


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
