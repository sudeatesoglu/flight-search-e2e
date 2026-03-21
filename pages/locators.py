from selenium.webdriver.common.by import By

class HomePageLocators:
    """Locators for the Enuygun Home Page."""
    
    ORIGIN_INPUT = (By.CSS_SELECTOR, "[data-testid='endesign-flight-origin-autosuggestion-input']")
    DESTINATION_INPUT = (By.CSS_SELECTOR, "[data-testid='endesign-flight-destination-autosuggestion-input']")
    DEPARTURE_DATE = (By.CSS_SELECTOR, "[data-testid='enuygun-homepage-flight-departureDate-label']")
    RETURN_DATE = (By.CSS_SELECTOR, "[data-testid='enuygun-homepage-flight-returnDate-label']")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "[data-testid='enuygun-homepage-flight-submitButton']")
    ORIGIN_FIRST_OPTION = (By.CSS_SELECTOR, "[data-testid='endesign-flight-origin-autosuggestion-option-item-0']")
    DESTINATION_FIRST_OPTION = (By.CSS_SELECTOR, "[data-testid='endesign-flight-destination-autosuggestion-option-item-0']")
    HOTEL_CHECKBOX_CHECKED = (By.CSS_SELECTOR, "[data-testid='flight-oneWayCheckbox-checked-label']")
    
    @staticmethod
    def get_date_locator(date_string: str) -> tuple[str, str]:
        """
        Dynamically constructs an XPath locator for a specific calendar day.
        
        Args:
            date_string (str): The target date string as present in the generic element title.
        
        Returns:
            tuple[str, str]: A formatted locator tuple.
        """
        return (By.XPATH, f"(//button[@title='{date_string}'])[last()]")


class FlightResultPageLocators:
    """Locators for the Enuygun Flight Search Results Page."""
    
    FLIGHT_CARDS = (By.CSS_SELECTOR, ".flight-item__wrapper")
    ACCORDION_PANEL = (By.CSS_SELECTOR, "div.ctx-filter-departure-return-time")
    SLIDER_TRACK = (By.XPATH, "(//div[contains(@class, 'rc-slider')])[1]")
    LEFT_HANDLE = (By.XPATH, "(//div[contains(@class, 'rc-slider-handle-1')])[1]")
    RIGHT_HANDLE = (By.XPATH, "(//div[contains(@class, 'rc-slider-handle-2')])[1]")
    DEPARTURE_TIMES = (By.CSS_SELECTOR, "[data-testid='departureTime']")
    LOADER_SPINNER = (By.CSS_SELECTOR, ".weg-loader")
