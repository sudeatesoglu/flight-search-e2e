import os
import pytest
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_execution.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Pytest Hooks for Reporting
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # Attach the report to the item for the specific phase
    setattr(item, "rep_" + rep.when, rep)


# WebDriver Fixture
@pytest.fixture(scope="function")
def driver(request):
    logger.info(f"Setting up WebDriver for test: {request.node.name}")
    
    # Setup Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Yield the driver to the test function
    yield driver
    
    # Check if the test failed during the 'call' phase
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        logger.error(f"Test failed: {request.node.name}. Capturing screenshot...")
        
        # Ensure screenshots exists
        os.makedirs("screenshots", exist_ok=True)
        
        # Generate unique timestamp and filepath
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f"{request.node.name}_{timestamp}.png"
        screenshot_path = os.path.join("screenshots", screenshot_filename)
        
        # Save screenshot
        driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved to: {screenshot_path}")
    
    # Teardown, quit the driver cleanly
    logger.info(f"Tearing down WebDriver for test: {request.node.name}")
    driver.quit()