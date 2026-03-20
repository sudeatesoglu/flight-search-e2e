from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage, ElementTimeoutException

class FlightResultPage(BasePage):
    """Page Object for the Enuygun Flight Search Results Page."""

    # Locators
    FILTER_TIME_10_TO_18 = (By.XPATH, "//label[contains(text(), '10:00 - 18:00')]")
    FLIGHT_CARDS = (By.XPATH, "//div[contains(@class, 'flight-card')]")
    DEPARTURE_TIMES = (By.CSS_SELECTOR, ".departure-time")
    LOADER_SPINNER = (By.CSS_SELECTOR, ".loading-spinner")

    def wait_for_results_to_load(self):
        """Wait for the flight results to appear on the screen."""
        logger.info("Waiting for flight result cards to load...")
        try:
            self.wait.until(EC.presence_of_all_elements_located(self.FLIGHT_CARDS))
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

    def apply_departure_time_filter(self):
        """Apply the 10:00 AM - 6:00 PM time filter."""
        logger.info("Applying Departure Time filter: 10:00 - 18:00 (10:00 AM - 6:00 PM).")
        self.click_element(self.FILTER_TIME_10_TO_18)
        self.wait_for_loader_to_disappear()

    def get_departure_times(self) -> list:
        """Gather all departure times currently displayed in the flight cards."""
        logger.info("Retrieving all departure times from displayed flight cards.")
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located(self.DEPARTURE_TIMES))
            
            times = [element.text.strip() for element in elements if element.text.strip()]
            logger.info(f"Retrieved {len(times)} departure times.")
            return times
        except TimeoutException as e:
            logger.error("Could not find any departure times on the page.")
            raise ElementTimeoutException("Departure time elements not found.") from e