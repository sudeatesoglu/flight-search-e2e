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
    ROUND_TRIP_RADIO = (By.CSS_SELECTOR, "[data-testid='search-round-trip-input']")
    
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

    # Filtering Panel
    ACCORDION_PANEL = (By.CSS_SELECTOR, "div.ctx-filter-departure-return-time")
    SLIDER_TRACK = (By.XPATH, "(//div[contains(@class, 'rc-slider')])[1]")
    LEFT_HANDLE = (By.XPATH, "(//div[contains(@class, 'rc-slider-handle-1')])[1]")
    RIGHT_HANDLE = (By.XPATH, "(//div[contains(@class, 'rc-slider-handle-2')])[1]")
    DEPARTURE_TIMES = (By.CSS_SELECTOR, "[data-testid='departureTime']")
    AIRLINE_ACCORDION = (By.CSS_SELECTOR, "div.ctx-filter-airline")
    THY_CHECKBOX = (By.CSS_SELECTOR, "input#TKairlines")

    # Flight Cards
    FLIGHT_CARDS = (By.CSS_SELECTOR, ".flight-item__wrapper")
    FLIGHT_CARD_AIRLINE_NAME = (By.CSS_SELECTOR, ".summary-marketing-airlines")
    FLIGHT_CARD_PRICE = (By.CSS_SELECTOR, "[data-testid='flightInfoPrice']")
    SELECT_FIRST_FLIGHT_BTN = (By.CSS_SELECTOR, "button.action-select-btn")
    RETURN_SELECT_BTNS = (By.CSS_SELECTOR, ".flight-list-return button.action-select-btn")
    FIRST_PACKAGE_SELECTION = (By.XPATH, "(//div[contains(@class, 'provider-package__item')])[1]")
    PACKAGE_ITEMS = (By.CSS_SELECTOR, "div.provider-package__item")
    PROVIDER_SELECT_BTN = (By.CSS_SELECTOR, "[data-testid='providerSelectBtn']")

    LOADER_SPINNER = (By.CSS_SELECTOR, ".weg-loader")


class PassengerInfoPageLocators:
    """Locators for the Enuygun Checkout / Passenger Information Page."""
    
    # Contact Information
    CONTACT_EMAIL = (By.CSS_SELECTOR, "#contact_email")
    CONTACT_PHONE = (By.CSS_SELECTOR, "#contact_cellphone")
    
    # Passenger Details
    FIRST_NAME = (By.CSS_SELECTOR, "[data-testid='reservation-passenger-name-input']")
    LAST_NAME = (By.CSS_SELECTOR, "[data-testid='reservation-passenger-surname-input']")
    
    BIRTH_DAY = (By.CSS_SELECTOR, "#birthDateDay_0")
    BIRTH_MONTH = (By.CSS_SELECTOR, "#birthDateMonth_0")
    BIRTH_YEAR = (By.CSS_SELECTOR, "#birthDateYear_0")
    
    ID_NUMBER = (By.CSS_SELECTOR, "[data-testid='reservation-publicid-TR-input']")
    
    GENDER_FEMALE = (By.XPATH, "//label[contains(., 'Kadın') or contains(., 'Female')]")
    GENDER_MALE = (By.XPATH, "//label[contains(., 'Erkek') or contains(., 'Male')]")
    # GENDER_MALE = (By.CSS_SELECTOR, "div.col-md-6 div:nth-of-type(1) > label")
    # GENDER_FEMALE = (By.CSS_SELECTOR, "div.col-md-6 div:nth-of-type(2) > label")
    
    CONTINUE_BTN = (By.CSS_SELECTOR, "#continue-button")
