from loguru import logger
from pages.base_page import BasePage
from pages.locators import PassengerInfoPageLocators

class PassengerInfoPage(BasePage):
    """Page Object for the Passenger Information and Checkout Page."""

    def fill_contact_info(self, email: str, phone: str) -> None:
        """Fill out the buyer's contact email and phone number."""
        logger.info(f"Filling contact info -> Email: {email}, Phone: {phone}")
        self.input_text(PassengerInfoPageLocators.CONTACT_EMAIL, email)
        self.input_text(PassengerInfoPageLocators.CONTACT_PHONE, phone)

    def fill_passenger_details(self, first_name: str, last_name: str, day: str, month: str, year: str, id_number: str, gender: str = "Female") -> None:
        """Fill out the specific passenger details."""
        logger.info(f"Filling passenger info -> Name: {first_name} {last_name}, TC: {id_number}")
        
        self.input_text(PassengerInfoPageLocators.FIRST_NAME, first_name)
        self.input_text(PassengerInfoPageLocators.LAST_NAME, last_name)
        
        self.input_text(PassengerInfoPageLocators.BIRTH_DAY, day)
        self.input_text(PassengerInfoPageLocators.BIRTH_MONTH, month)
        self.input_text(PassengerInfoPageLocators.BIRTH_YEAR, year)
        
        self.input_text(PassengerInfoPageLocators.ID_NUMBER, id_number)
        
        if gender.lower() == "female" or gender.lower() == "kadın":
            logger.info("Selecting gender: Female")
            self.click_element_with_js(PassengerInfoPageLocators.GENDER_FEMALE)
        else:
            logger.info("Selecting gender: Male")
            self.click_element_with_js(PassengerInfoPageLocators.GENDER_MALE)

    def proceed_to_payment(self) -> None:
        """Click the continue button to navigate to the payment screen."""
        logger.info("Clicking 'Ödemeye İlerle' (Continue to Payment) button.")
        self.click_element_with_js(PassengerInfoPageLocators.CONTINUE_BTN)
