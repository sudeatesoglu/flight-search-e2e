from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage, ElementTimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

class FlightResultPage(BasePage):
    """Page Object for the Enuygun Flight Search Results Page."""

    # Locators
    FLIGHT_CARDS = (By.CSS_SELECTOR, ".flight-item__wrapper")
    ACCORDION_PANEL = (By.CSS_SELECTOR, "div.ctx-filter-departure-return-time")
    SLIDER_TRACK = (By.XPATH, "(//div[contains(@class, 'rc-slider')])[1]")
    LEFT_HANDLE = (By.XPATH, "(//div[contains(@class, 'rc-slider-handle-1')])[1]")
    RIGHT_HANDLE = (By.XPATH, "(//div[contains(@class, 'rc-slider-handle-2')])[1]")
    DEPARTURE_TIMES = (By.CSS_SELECTOR, "[data-testid='departureTime']")
    LOADER_SPINNER = (By.CSS_SELECTOR, ".weg-loader")

    def wait_for_results_to_load(self):
        """Wait for the flight results to appear on the screen."""
        logger.info("Waiting for flight result cards to load...")
        try:
            WebDriverWait(self.driver, 30).until(EC.presence_of_all_elements_located(self.FLIGHT_CARDS))
            logger.info("Flight result cards loaded successfully.")
        except TimeoutException as e:
            logger.error(f"TimeoutException: Flight results {self.FLIGHT_CARDS} did not load within {self.timeout} seconds.")
            raise ElementTimeoutException("Flight results failed to load.") from e


    def wait_for_loader_to_disappear(self):
        """Wait for the loader to disappear on the screen."""
        logger.debug("Checking if loader is present and waiting for it to disappear...")
        try:
            self.wait.until(EC.invisibility_of_element_located(self.LOADER_SPINNER))
            logger.info("Loader disappeared, DOM is ready.")
        except TimeoutException:
            logger.warning("Loader did not disappear or took too long. Proceeding anyway...")


    def apply_departure_time_filter(self, start_time: str, end_time: str):
        """
        Apply a dynamic departure time filter using ActionChains.
        Utilizes a pragmatic approach combining loader checks and brief settling pauses 
        to bypass React's Virtual DOM diffing engine and slider bot protections.
        """
        import time
        
        def time_to_mins(t_str: str) -> int:
            h, m = map(int, t_str.split(':'))
            return h * 60 + m

        target_start_mins = time_to_mins(start_time)
        target_end_mins = time_to_mins(end_time)

        logger.info(f"Applying Departure Time filter: {start_time} - {end_time} ({target_start_mins} - {target_end_mins} mins).")
        
        logger.info("Opening the accordion panel.")
        self.click_element_with_actions(self.ACCORDION_PANEL)
        
        time.sleep(1)

        slider_track = self.wait.until(EC.visibility_of_element_located(self.SLIDER_TRACK))
        slider_width = slider_track.size['width']
        max_minutes = 1439.0

        # left handle (start time)
        left_handle = self.find_element(self.LEFT_HANDLE)
        current_left = int(left_handle.get_attribute("aria-valuenow"))
        
        if current_left < target_start_mins:
            x_offset_left = int(((target_start_mins - current_left) / max_minutes) * slider_width)
            logger.info(f"Human-like dragging left handle to {start_time} (Offset: {x_offset_left}px).")
            
            action = ActionChains(self.driver)
            action.click_and_hold(left_handle).pause(0.5).move_by_offset(x_offset_left, 0).pause(0.5).release().perform()
            
            # After dragging, wait for potential loader and add a brief pause to allow React to settle before next action
            time.sleep(1) 
            self.wait_for_loader_to_disappear()
            time.sleep(1.5)

        # right handle (end time)
        right_handle = self.find_element(self.RIGHT_HANDLE)
        current_right = int(right_handle.get_attribute("aria-valuenow"))
        
        if current_right > target_end_mins:
            x_offset_right = int(((current_right - target_end_mins) / max_minutes) * slider_width)
            logger.info(f"Human-like dragging right handle to {end_time} (Offset: {-x_offset_right}px).")
            
            action = ActionChains(self.driver)
            action.click_and_hold(right_handle).pause(0.5).move_by_offset(-x_offset_right, 0).pause(0.5).release().perform()
            
            time.sleep(1)
            self.wait_for_loader_to_disappear()
            time.sleep(1.5)


    def get_departure_times(self) -> list:
        """Gather all departure times currently displayed in the flight cards."""
        logger.info("Retrieving all departure times from displayed flight cards.")
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located(self.DEPARTURE_TIMES))
            
            times = [element.text.strip() for element in elements if element.is_displayed() and element.text.strip()]

            logger.info(f"Retrieved {len(times)} visible departure times.")
            return times
        except TimeoutException as e:
            logger.error("Could not find any departure times on the page.")
            raise ElementTimeoutException("Departure time elements not found.") from e