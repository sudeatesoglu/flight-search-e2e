import os
import pytest
from datetime import datetime
import allure
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from core.config import Config

# Configure Loguru globally to not add a new file handler on every test iteration
logger.add('test_execution.log', rotation='10 MB', level='INFO')

# CLI Options for Test Parameters
def pytest_addoption(parser):
    """Adds custom command-line options for test configuration."""
    parser.addoption("--origin", action="store", default="Istanbul", help="Origin city (e.g., Istanbul)")
    parser.addoption("--destination", action="store", default="Lefkosa", help="Destination city (e.g., Lefkosa)")
    parser.addoption("--dep-date", action="store", default="2026-04-15", help="Departure date (YYYY-MM-DD)")
    parser.addoption("--ret-date", action="store", default="2026-04-20", help="Return date (YYYY-MM-DD)")
    parser.addoption("--start-time", action="store", default="10:00", help="Filter start time (e.g., 10:00)")
    parser.addoption("--end-time", action="store", default="18:00", help="Filter end time (e.g., 18:00)")

@pytest.fixture
def origin(request):
    return request.config.getoption("--origin")

@pytest.fixture
def destination(request):
    return request.config.getoption("--destination")

@pytest.fixture
def dep_date(request):
    return request.config.getoption("--dep-date")

@pytest.fixture
def ret_date(request):
    return request.config.getoption("--ret-date")

@pytest.fixture
def start_time(request):
    return request.config.getoption("--start-time")

@pytest.fixture
def end_time(request):
    return request.config.getoption("--end-time")


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
            
            # Attach to Allure report
            allure.attach.file(
                screenshot_path,
                name=f"Screenshot_{item.name}",
                attachment_type=allure.attachment_type.PNG
            )
            
            # Log the error and screenshot capture
            logger.error(f"Test failed: {item.name}. Screenshot saved to {screenshot_path}")

# WebDriver Fixture
@pytest.fixture(scope="function")
def driver(request):
    browser_name = Config.BROWSER.lower()
    logger.info(f"Starting {browser_name} browser for test: {request.node.name}")
    
    if browser_name == "firefox":
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.set_window_size(1920, 1080)
    else:
        # Setup Chrome options for headless mode
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize the Chrome driver
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Yield the driver to the test function
    yield driver
    
    # Teardown, quit the driver cleanly
    logger.info(f"Quitting browser for test: {request.node.name}")
    driver.quit()