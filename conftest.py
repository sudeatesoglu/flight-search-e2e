import os
import pytest
from datetime import datetime
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configure Loguru globally to not add a new file handler on every test iteration
logger.add('test_execution.log', rotation='10 MB', level='INFO')

# Pytest Hook for Reporting and Screenshot on Failure
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # Attach the report to the item for the specific phase
    setattr(item, "rep_" + rep.when, rep)
    
    # Check if the test failed during the 'call' phase
    if rep.when == "call" and rep.failed:
        # Retrieve the driver instance from the fixture
        driver = item.funcargs.get("driver")
        if driver:
            # Ensure screenshots directory exists
            os.makedirs("screenshots", exist_ok=True)
            
            # Generate unique timestamp and filepath
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f"{item.name}_{timestamp}.png"
            screenshot_path = os.path.join("screenshots", screenshot_filename)
            
            # Save screenshot
            driver.save_screenshot(screenshot_path)
            
            # Log the error and screenshot capture
            logger.error(f"Test failed: {item.name}. Screenshot saved to {screenshot_path}")

# WebDriver Fixture
@pytest.fixture(scope="function")
def driver(request):
    logger.info(f"Starting browser for test: {request.node.name}")
    
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
    
    # Teardown, quit the driver cleanly
    logger.info(f"Quitting browser for test: {request.node.name}")
    driver.quit()