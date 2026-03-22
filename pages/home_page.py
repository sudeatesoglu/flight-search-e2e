from loguru import logger
from pages.base_page import BasePage, ElementTimeoutException
from pages.locators import HomePageLocators


class HomePage(BasePage):
    """Page Object for the Enuygun Home Page."""

    def go_to(self, url: str) -> None:
        """
        Navigate to the specified URL.
        
        Args:
            url (str): The full URL mapped to the application.
        """
        logger.info(f"Navigating to Home Page: {url}")
        self.driver.get(url)


    def enter_origin(self, city: str) -> None:
        """
        Enter the origin city and select the first suggestion.

        Args:
            city (str): The origin destination string.
        """
        logger.info(f"Setting Origin city to: {city}")
        self.input_text(HomePageLocators.ORIGIN_INPUT, city)
        self.click_element(HomePageLocators.ORIGIN_FIRST_OPTION)


    def enter_destination(self, city: str) -> None:
        """
        Enter the destination city and select the first suggestion.

        Args:
            city (str): The target destination string.
        """
        logger.info(f"Setting Destination city to: {city}")
        self.input_text(HomePageLocators.DESTINATION_INPUT, city)
        self.click_element(HomePageLocators.DESTINATION_FIRST_OPTION)


    def select_departure_date(self, date_string: str) -> None:
        """
        Select a departure date from the datepicker.
        Opens the calendar and clicks the exact date element based on the provided date_string.
        
        Args:
            date_string (str): The departure date localized string used to locate the calendar item.
        """
        logger.info("Opening the Departure Date calendar.")
        self.click_element(HomePageLocators.DEPARTURE_DATE)
        
        logger.info(f"Selecting Departure Date: {date_string}")
        date_locator = HomePageLocators.get_date_locator(date_string)
        self.click_element(date_locator)


    def select_return_date(self, date_string: str) -> None:
        """
        Select a return date from the datepicker.
        Clicks the return date input to ensure the round-trip mode is active, then selects the date.
        
        Args:
            date_string (str): The return date localized string used to locate the calendar item.
        """
        logger.info("Opening the Return Date calendar.")
        self.click_element(HomePageLocators.RETURN_DATE)
        
        logger.info(f"Selecting Return Date: {date_string}")
        date_locator = HomePageLocators.get_date_locator(date_string)
        self.click_element(date_locator)


    def uncheck_hotel_offer(self) -> None:
        """
        Ensures the 'List hotels for these dates' checkbox is unchecked.
        Prevents the search from opening in a new tab for hotel listing.
        """
        logger.info("Checking if the 'Hotel offer' checkbox is selected.")
        try:
            checked_elements = self.driver.find_elements(*HomePageLocators.HOTEL_CHECKBOX_CHECKED)
            
            if len(checked_elements) > 0:
                logger.info("Hotel offer is currently CHECKED. Unchecking it to avoid new tabs.")
                self.click_element(HomePageLocators.HOTEL_CHECKBOX_CHECKED)
            else:
                logger.info("Hotel offer is already UNCHECKED. Good to go.")
        except Exception as e:
            logger.warning(f"Error while checking the Hotel Checkbox: {e}")


    def click_search(self) -> None:
        """Click the main search button to find flights."""
        logger.info("Clicking the flight search button.")
        self.click_element(HomePageLocators.SEARCH_BUTTON)


    def is_round_trip(self) -> bool:
        """Returns True if the 'Gidiş-dönüş' (Round-trip) radio button is active."""
        logger.info("Checking if 'Gidiş-dönüş' (Round-trip) is selected on the UI.")
        try:
            radio_input = self.find_element(HomePageLocators.ROUND_TRIP_RADIO)
            is_checked = radio_input.get_attribute("checked") is not None
            logger.info(f"Round-trip status based on radio button: {is_checked}")
            return is_checked
        except ElementTimeoutException:
            logger.warning("Could not find the round-trip radio button.")
            return False
        

    def search_flights(self, origin: str, destination: str, dep_date: str, ret_date: str) -> None:
        """
        Helper method to execute a full round-trip search flow.
        
        Args:
            origin (str): Origin departure city.
            destination (str): Target arrival city.
            dep_date (str): Expected departure date format logic.
            ret_date (str): Expected return date format logic.
        """
        self.enter_origin(origin)
        self.enter_destination(destination)
        self.select_departure_date(dep_date)
        self.select_return_date(ret_date)
        self.uncheck_hotel_offer()
        self.click_search()
