from loguru import logger
from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class HomePage(BasePage):
    """Page Object for the Enuygun Home Page."""
    
    # Locators
    ORIGIN_INPUT = (By.ID, "OriginInput")
    DESTINATION_INPUT = (By.ID, "DestinationInput")
    DEPARTURE_DATE = (By.ID, "DepartureDate")
    RETURN_DATE = (By.ID, "ReturnDate")
    SEARCH_BUTTON = (By.CLASS_NAME, "primary-btn")
    
    # Generic option selector for dropdowns
    FIRST_AUTOCOMPLETE_OPTION = (By.XPATH, "//ul[contains(@class, 'suggestion-list')]//li[1]")

    def go_to(self, url: str):
        """Navigate to the specified URL."""
        logger.info(f"Navigating to Home Page: {url}")
        self.driver.get(url)

    def enter_origin(self, city: str):
        """Enter the origin city and select the first suggestion."""
        logger.info(f"Setting Origin city to: {city}")
        self.input_text(self.ORIGIN_INPUT, city)
        self.click_element(self.FIRST_AUTOCOMPLETE_OPTION)

    def enter_destination(self, city: str):
        """Enter the destination city and select the first suggestion."""
        logger.info(f"Setting Destination city to: {city}")
        self.input_text(self.DESTINATION_INPUT, city)
        self.click_element(self.FIRST_AUTOCOMPLETE_OPTION)

    def select_departure_date(self, date_string: str):
        """
        Select a departure date from the datepicker.
        Opens the calendar and clicks the exact date element based on the provided date_string.
        """
        logger.info("Opening the Departure Date calendar.")
        self.click_element(self.DEPARTURE_DATE)
        
        logger.info(f"Selecting Departure Date: {date_string}")
        date_locator = (By.XPATH, f"//div[@data-date='{date_string}']")
        self.click_element(date_locator)

    def select_return_date(self, date_string: str):
        """
        Select a return date from the datepicker.
        Opens the calendar and clicks the exact date element based on the provided date_string.
        """
        logger.info("Opening the Return Date calendar.")
        self.click_element(self.RETURN_DATE)
        
        logger.info(f"Selecting Return Date: {date_string}")
        date_locator = (By.XPATH, f"//div[@data-date='{date_string}']")
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