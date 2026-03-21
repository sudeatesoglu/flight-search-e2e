from loguru import logger
from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class HomePage(BasePage):
    """Page Object for the Enuygun Home Page."""
    
    # Locators
    ORIGIN_INPUT = (By.CSS_SELECTOR, "[data-testid='endesign-flight-origin-autosuggestion-input']")
    DESTINATION_INPUT = (By.CSS_SELECTOR, "[data-testid='endesign-flight-destination-autosuggestion-input']")
    DEPARTURE_DATE = (By.CSS_SELECTOR, "[data-testid='enuygun-homepage-flight-departureDate-datepicker-input']")
    RETURN_DATE = (By.CSS_SELECTOR, "[data-testid='enuygun-homepage-flight-returnDate-datepicker-input']")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "[data-testid='enuygun-homepage-flight-submitButton']")
    ORIGIN_FIRST_OPTION = (By.CSS_SELECTOR, "[data-testid='endesign-flight-origin-autosuggestion-option-item-0")
    DESTINATION_FIRST_OPTION = (By.CSS_SELECTOR, "[data-testid='endesign-flight-destination-autosuggestion-option-item-0")

    def go_to(self, url: str):
        """Navigate to the specified URL."""
        logger.info(f"Navigating to Home Page: {url}")
        self.driver.get(url)

    def enter_origin(self, city: str):
        logger.info(f"Setting Origin city to: {city}")
        self.input_text(self.ORIGIN_INPUT, city)
        self.click_element(self.ORIGIN_FIRST_OPTION)

    def enter_destination(self, city: str):
        logger.info(f"Setting Destination city to: {city}")
        self.input_text(self.DESTINATION_INPUT, city)
        self.click_element(self.DESTINATION_FIRST_OPTION)

    def select_departure_date(self, date_string: str):
        """
        Select a departure date from the datepicker.
        Opens the calendar and clicks the exact date element based on the provided date_string.
        """
        logger.info("Opening the Departure Date calendar.")
        self.click_element(self.DEPARTURE_DATE)
        
        logger.info(f"Selecting Departure Date: {date_string}")
        date_locator = (By.XPATH, f"(//button[@title='{date_string}'])[last()]")
        self.click_element(date_locator)

    def select_return_date(self, date_string: str):
        """
        Select a return date from the datepicker.
        Clicks the return date input to ensure the round-trip mode is active, then selects the date.
        """
        logger.info("Opening the Return Date calendar.")
        self.click_element(self.RETURN_DATE)
        
        logger.info(f"Selecting Return Date: {date_string}")
        date_locator = (By.XPATH, f"(//button[@title='{date_string}'])[last()]")
        self.click_element(date_locator)

    def click_search(self):
        """Click the main search button to find flights."""
        logger.info("Clicking the flight search button.")
        self.click_element(self.SEARCH_BUTTON)

    def search_flights(self, origin: str, destination: str, dep_date: str, ret_date: str):
        """Helper method to execute a full round-trip search flow."""
        self.enter_origin(origin)
        self.enter_destination(destination)
        self.select_departure_date(dep_date)
        self.select_return_date(ret_date)
        self.click_search()