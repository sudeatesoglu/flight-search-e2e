from loguru import logger
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class ElementTimeoutException(Exception):
    """Custom exception raised when an element cannot be found within the specified timeout."""
    pass

class BasePage:
    """Base class providing standard Selenium operations and explicit waits for all page objects."""

    def __init__(self, driver, timeout=15):
        """
        Initialize the BasePage with a WebDriver instance and a default explicit wait timeout.
        
        :param driver: Selenium WebDriver instance
        :param timeout: Maximum time to wait for a condition (in seconds)
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(self.driver, self.timeout)


    def find_element(self, locator):
        """
        Wait for an element to be present in the DOM and return it.
        
        :param locator: Tuple of (By locator type, locator string)
        :return: WebElement found
        """
        logger.debug(f"Attempting to find element with locator: {locator}")
        try:
            element = self.wait.until(EC.presence_of_element_located(locator))
            logger.info(f"Successfully found element: {locator}")
            return element
        except TimeoutException as e:
            logger.error(f"TimeoutException: Could not find element {locator} within {self.timeout} seconds.")
            raise ElementTimeoutException(f"Element {locator} not present.") from e


    def click_element(self, locator):
        """
        Wait until an element is clickable and perform a click action.
        
        :param locator: Tuple of (By locator type, locator string)
        """
        logger.debug(f"Attempting to click element with locator: {locator}")
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
            logger.info(f"Successfully clicked element: {locator}")
        except TimeoutException as e:
            logger.error(f"TimeoutException: Element {locator} is not clickable within {self.timeout} seconds.")
            raise ElementTimeoutException(f"Element {locator} not clickable.") from e


    def input_text(self, locator, text):
        """
        Wait until an element is visible, clear its existing content, and input new text.
        
        :param locator: Tuple of (By locator type, locator string)
        :param text: The text string to input
        """
        logger.debug(f"Attempting to input text '{text}' into element: {locator}")
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            element.clear()
            element.send_keys(text)
            logger.info(f"Successfully inputted text into element: {locator}")
        except TimeoutException as e:
            logger.error(f"TimeoutException: Could not input text. Element {locator} not visible within {self.timeout}s.")
            raise ElementTimeoutException(f"Element {locator} not visible for text input.") from e


    def get_text(self, locator):
        """
        Wait until an element is visible and retrieve its text content.
        
        :param locator: Tuple of (By locator type, locator string)
        :return: String text of the element
        """
        logger.debug(f"Attempting to get text from element: {locator}")
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            text = element.text
            logger.info(f"Successfully retrieved text '{text}' from element: {locator}")
            return text
        except TimeoutException as e:
            logger.error(f"TimeoutException: Could not get text. Element {locator} not visible within {self.timeout}s.")
            raise ElementTimeoutException(f"Element {locator} not visible for getting text.") from e