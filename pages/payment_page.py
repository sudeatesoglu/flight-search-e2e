from loguru import logger
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from pages.locators import PaymentPageLocators

class PaymentPage(BasePage):
    """Page Object for the Payment Page."""

    def handle_membership_popup(self) -> None:
        """Closes the membership/login popup if it aggressively appears on the payment page."""
        logger.info("Checking for membership pop-up...")
        try:
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(PaymentPageLocators.MEMBERSHIP_DIALOG_CLOSE)
            )
            self.click_element_with_js(PaymentPageLocators.MEMBERSHIP_DIALOG_CLOSE)
            logger.info("Membership pop-up detected and closed successfully.")
        except TimeoutException:
            logger.info("No membership pop-up appeared. Proceeding safely.")


    def fill_credit_card(self, card_no: str, month_idx: str, year_idx: str, cvv: str) -> None:
        """
        Fills out the credit card form using Enuygun's custom dropdown structure.
        """
        logger.info("Filling credit card details...")
        self.input_text(PaymentPageLocators.CARD_NUMBER, card_no)
        
        self.click_element_with_js(PaymentPageLocators.CARD_MONTH_INPUT)
        self.click_element_with_js(PaymentPageLocators.get_month_option(month_idx))
        
        self.click_element_with_js(PaymentPageLocators.CARD_YEAR_INPUT)
        self.click_element_with_js(PaymentPageLocators.get_year_option(year_idx))
        
        self.input_text(PaymentPageLocators.CVV, cvv)

    
    def verify_additional_payment_options(self) -> None:
        """Clicks and verifies the installment table and discount code areas."""
        logger.info("Verifying Installment Table and Discount Code options...")
        try:
            self.click_element_with_js(PaymentPageLocators.INSTALLMENT_TABLE)
            logger.info("Installment table expanded.")
            self.click_element_with_js(PaymentPageLocators.INSTALLMENT_TABLE_CLOSE)
            logger.info("Installment table closed.")
            self.click_element_with_js(PaymentPageLocators.DISCOUNT_BOX)
            logger.info("Discount box clicked.")
        except Exception:
            logger.warning("Installment or Discount options not fully visible or clickable.")


    def submit_payment(self) -> None:
        """Clicks the final payment submit button to complete the critical path."""
        logger.info("Clicking the final 'Submit Payment' button.")
        self.click_element_with_js(PaymentPageLocators.SUBMIT_BUTTON)
        