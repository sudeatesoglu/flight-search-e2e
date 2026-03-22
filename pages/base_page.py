from loguru import logger
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

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


    def click_element_with_actions(self, locator):
        """
        Simulate physical mouse click at the exact center coordinates of the element.

        :param locator: Tuple of (By locator type, locator string)
        """
        logger.debug(f"Attempting to click with ActionChains: {locator}")
        try:
            element = self.wait.until(EC.presence_of_element_located(locator))
            ActionChains(self.driver).move_to_element(element).click().perform()
            logger.info(f"Successfully clicked element with ActionChains: {locator}")
        except TimeoutException as e:
            logger.error(f"TimeoutException: Element {locator} not present for Action click.")
            raise ElementTimeoutException(f"Element {locator} not present.") from e
        
    
    def click_element_with_js(self, locator):
        """
        Click an element using JavaScript execution.
            
        :param locator: Tuple of (By locator type, locator string)
        """
        logger.debug(f"Attempting to click with JS: {locator}")
        try:
            element = self.wait.until(EC.presence_of_element_located(locator))
            self.driver.execute_script("arguments[0].click();", element)
            logger.info(f"Successfully clicked element with JS: {locator}")
        except TimeoutException as e:
            logger.error(f"TimeoutException: Element {locator} not present for JS click.")
            raise ElementTimeoutException(f"Element {locator} not present.") from e


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
        

    def select_dropdown(self, locator, value: str):
        """
        Wait until a <select> element is visible and select an option.

        :param locator: Tuple of (By locator type, locator string)
        :param value: The value or text to select
        """
        logger.debug(f"Attempting to select '{value}' from dropdown: {locator}")
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            select = Select(element)
            
            try:
                select.select_by_value(value)
            except:
                select.select_by_visible_text(value)
                
            logger.info(f"Successfully selected '{value}' from {locator}")
        except Exception as e:
            logger.error(f"Failed to select '{value}' from dropdown {locator}. Exception: {e}")
            raise ElementTimeoutException(f"Could not select {value} from {locator}") from e
        