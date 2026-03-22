import pytest
from datetime import datetime
from loguru import logger

from pages.home_page import HomePage
from pages.flight_result_page import FlightResultPage
from pages.passenger_info_page import PassengerInfoPage
from core.config import Config

# Constants
TIME_FORMAT = "%H:%M"
SCREENSHOT_DIR = "screenshots"
TEST_ORIGIN = "Istanbul"
TEST_DESTINATION = "Ankara"
TEST_DEP_DATE = "2026-04-15"
TEST_RET_DATE = "2026-04-20"
TEST_START_TIME = "10:00"
TEST_END_TIME = "18:00"
TURKISH_AIRLINES_NAMES = ("Türk Hava Yolları", "THY")


@pytest.mark.parametrize(
    "origin, destination, dep_date, ret_date, start_time, end_time",
    [
        (TEST_ORIGIN, TEST_DESTINATION, TEST_DEP_DATE, TEST_RET_DATE, TEST_START_TIME, TEST_END_TIME)
    ]
)
def test_case_1_basic_flight_search_and_time_filter(
    driver, origin, destination, dep_date, ret_date, start_time, end_time
):
    """Search for flights and validate departure times fall within filter range."""
    logger.info(f"Starting Case 1: {origin} to {destination} | Filter: {start_time}-{end_time}")
    
    home_page = HomePage(driver)
    results_page = FlightResultPage(driver)
    
    home_page.go_to(Config.BASE_URL)
    home_page.search_flights(origin, destination, dep_date, ret_date)
    results_page.wait_for_results_to_load()
    results_page.apply_departure_time_filter(start_time, end_time)
    
    departure_times = results_page.get_departure_times()
    assert departure_times, "No flights found after applying time filter."
    
    _validate_departure_times(departure_times, start_time, end_time)
    
    _save_success_screenshot(driver, "Case1", start_time, end_time)
    logger.info("Case 1 completed successfully")


@pytest.mark.parametrize(
    "origin, destination, dep_date, ret_date, start_time, end_time",
    [
        (TEST_ORIGIN, TEST_DESTINATION, TEST_DEP_DATE, TEST_RET_DATE, TEST_START_TIME, TEST_END_TIME)
    ]
)
def test_case_2_turkish_airlines_price_sorting(
    driver, origin, destination, dep_date, ret_date, start_time, end_time
):
    """Validate Turkish Airlines filtering and price sorting in ascending order."""
    logger.info(f"Starting Case 2: {origin} to {destination} - Turkish Airlines pricing")
    
    home_page = HomePage(driver)
    results_page = FlightResultPage(driver)
    
    home_page.go_to(Config.BASE_URL)
    home_page.search_flights(origin, destination, dep_date, ret_date)
    results_page.wait_for_results_to_load()
    results_page.apply_departure_time_filter(start_time, end_time)
    results_page.apply_airline_filter()
    
    airlines = results_page.get_displayed_airlines()
    prices = results_page.get_displayed_prices()
    
    assert airlines, "No airlines detected after filtering."
    assert prices, "No prices detected after filtering."
    
    _validate_turkish_airlines_only(airlines)
    _validate_prices_ascending(prices)
    
    _save_success_screenshot(driver, "Case2_THY", start_time, end_time)
    logger.info("Case 2 completed successfully")


@pytest.mark.parametrize(
    "origin, destination, dep_date, ret_date, email, phone, fname, lname, b_day, b_month, b_year, id_number, gender",
    [
        (TEST_ORIGIN, TEST_DESTINATION, TEST_DEP_DATE, TEST_RET_DATE, 
         "sude.test@gmail.com", "5551234567", "Sude", "Atesoglu", "04", "04", "2000", "12345678901", "Female")
    ]
)
def test_case_3_critical_path(
    driver, origin, destination, dep_date, ret_date, email, phone, fname, lname, b_day, b_month, b_year, id_number, gender
):
    logger.info("--- Starting Case 3: Critical Path (End-to-End Checkout Flow) ---")
    
    home_page = HomePage(driver)
    results_page = FlightResultPage(driver)
    passenger_page = PassengerInfoPage(driver)
    
    home_page.go_to(Config.BASE_URL)
    home_page.enter_origin(origin)
    home_page.enter_destination(destination)
    home_page.select_departure_date(dep_date)
    home_page.select_return_date(ret_date)
    home_page.uncheck_hotel_offer()
    
    is_round_trip_search = home_page.is_round_trip()
    
    home_page.click_search()
    results_page.wait_for_results_to_load()
    
    logger.info("Selecting the departure flight (Left Column)...")
    results_page.select_first_flight(is_return=False, is_final_flight=not is_round_trip_search)

    if is_round_trip_search:
        logger.info("Round-trip explicitly detected from Home Page. Selecting return flight (Right Column)...")
        results_page.select_first_flight(is_return=True, is_final_flight=True)
    else:
        logger.info("Single-trip detected. Proceeding directly to passenger info.")

    passenger_page.fill_contact_info(email, phone)
    passenger_page.fill_passenger_details(fname, lname, b_day, b_month, b_year, id_number, gender)
    
    passenger_page.proceed_to_payment()
    
    assert "odeme" in driver.current_url.lower() or "payment" in driver.current_url.lower(), \
        "Failed to reach the payment screen!"
    logger.info("Assertion Passed: Successfully reached the secure payment page.")

    _save_success_screenshot(driver, "Case3_CriticalPath", "E2E", "Done")
    logger.info("--- Case 3 Completed Successfully ---")
    

def _validate_departure_times(departure_times: list, start_time: str, end_time: str) -> None:
    """Validate all departure times fall within the specified range."""
    start_bound = datetime.strptime(start_time, TIME_FORMAT).time()
    end_bound = datetime.strptime(end_time, TIME_FORMAT).time()
    
    for time_str in departure_times:
        flight_time = datetime.strptime(time_str, TIME_FORMAT).time()
        assert start_bound <= flight_time <= end_bound, (
            f"Flight departure time {time_str} is outside allowed range {start_time}-{end_time}"
        )
    
    logger.info(f"Validated {len(departure_times)} flights within {start_time}-{end_time}")


def _validate_turkish_airlines_only(airlines: list) -> None:
    """Validate all airlines are Turkish Airlines."""
    for airline in airlines:
        assert any(name in airline for name in TURKISH_AIRLINES_NAMES), (
            f"Expected Turkish Airlines, but found: {airline}"
        )
    logger.info("All flights are Turkish Airlines")


def _validate_prices_ascending(prices: list) -> None:
    """Validate prices are sorted in ascending order."""
    assert prices == sorted(prices), (
        f"Prices not in ascending order.\nActual: {prices}\nExpected: {sorted(prices)}"
    )
    logger.info("Prices are correctly sorted in ascending order")


def _save_success_screenshot(driver, case_name: str, start_time: str, end_time: str) -> None:
    """Save screenshot with standardized naming."""
    time_suffix = start_time.replace(":", "") + "_" + end_time.replace(":", "")
    screenshot_name = f"{SCREENSHOT_DIR}/SUCCESS_{case_name}_{time_suffix}.png"
    driver.save_screenshot(screenshot_name)
    logger.info(f"Screenshot saved: {screenshot_name}")
