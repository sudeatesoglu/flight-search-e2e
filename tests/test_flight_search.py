import pytest
import allure
from datetime import datetime
from loguru import logger
from dataclasses import dataclass

from pages.home_page import HomePage
from pages.flight_result_page import FlightResultPage
from pages.passenger_info_page import PassengerInfoPage
from pages.payment_page import PaymentPage
from core.config import Config

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Constants
TIME_FORMAT = "%H:%M"
SCREENSHOT_DIR = "screenshots"
TURKISH_AIRLINES_NAMES = ("Türk Hava Yolları", "THY")

# Mock Data Classes for Passenger and Credit Card Information
@dataclass
class MockPassenger:
    """Mock verileri tutan modern ve temiz bir veri sınıfı."""
    email: str = "sude.test@gmail.com"
    phone: str = "5551234567"
    fname: str = "Sude"
    lname: str = "Atesoglu"
    id_number: str = "58880076462"
    b_day: str = "04"
    b_month: str = "04"
    b_year: str = "2000"
    gender: str = "Female"
    
@dataclass
class MockCreditCard:
    """Kredi kartı verilerini tutan sınıf."""
    cc_no: str = "4242424242424242"
    cc_month_idx: str = "0"
    cc_year_idx: str = "1"
    cc_cvv: str = "123"


@allure.epic("Flight Search System")
@allure.feature("Flight Search & Filter")
@allure.story("Filter by Departure Time")
@allure.title("Test Case 1: Departure Time Filtering ({origin} -> {destination})")
@allure.description("Perform a basic flight search and validate that all displayed flights fall within the selected departure time range.")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("layer", "e2e")
def test_case_1_basic_flight_search_and_time_filter(
    driver, origin, destination, dep_date, ret_date, start_time, end_time
):
    """Search for flights and validate departure times fall within filter range."""
    logger.info(f"Starting Case 1: {origin} to {destination} | Filter: {start_time}-{end_time}")
    
    with allure.step("Navigate to HomePage and Search"):
        home_page = HomePage(driver)
        results_page = FlightResultPage(driver)
        home_page.go_to(Config.BASE_URL)
        home_page.search_flights(origin, destination, dep_date, ret_date)
        
    with allure.step(f"Wait for results and Filter by Time ({start_time}-{end_time})"):
        results_page.wait_for_results_to_load()
        results_page.apply_departure_time_filter(start_time, end_time)
        
    with allure.step("Validate Departure Times"):
        departure_times = results_page.get_departure_times()
        assert departure_times, "No flights found after applying time filter."
        _validate_departure_times(departure_times, start_time, end_time)
    
    _save_success_screenshot(driver, "Case1", start_time, end_time)
    logger.info("Case 1 completed successfully")


@allure.epic("Flight Search System")
@allure.feature("Airline Specific Search")
@allure.story("Turkish Airlines Price Sorting")
@allure.title("Test Case 2: Turkish Airlines Price Sorting ({origin} -> {destination})")
@allure.description("Search for flights, filter by Turkish Airlines, strictly sort by cheapest price, and validate ascending order.")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("layer", "e2e")
def test_case_2_turkish_airlines_price_sorting(
    driver, origin, destination, dep_date, ret_date, start_time, end_time
):
    """Validate Turkish Airlines filtering and price sorting in ascending order."""
    logger.info(f"Starting Case 2: {origin} to {destination} - Turkish Airlines pricing")
    
    with allure.step("Search Flights and Wait for Loading"):
        home_page = HomePage(driver)
        results_page = FlightResultPage(driver)
        home_page.go_to(Config.BASE_URL)
        home_page.search_flights(origin, destination, dep_date, ret_date)
        results_page.wait_for_results_to_load()
        
    with allure.step("Apply Time and Airline Filters"):
        results_page.apply_departure_time_filter(start_time, end_time)
        results_page.apply_airline_filter()

    with allure.step("Sort results explicitly by cheapest price"):
        results_page.click_sort_by_price_ascending()
        
    with allure.step("Extract Metrics and Assert Validation"):
        airlines = results_page.get_displayed_airlines()
        prices = results_page.get_displayed_prices()
        
        assert airlines, "No airlines detected after filtering."
        assert prices, "No prices detected after filtering."
        
        _validate_turkish_airlines_only(airlines)
        _validate_prices_ascending(prices)
    
    _save_success_screenshot(driver, "Case2_THY", start_time, end_time)
    logger.info("Case 2 completed successfully")


@allure.epic("Flight Booking and Reservation")
@allure.feature("End to End Checkout")
@allure.story("Critical Path for Valid Users")
@allure.title("Test Case 3: Complete Critical User Path ({origin} -> {destination})")
@allure.description("Validates the entire process starting from search, selecting flights, entering passenger information, and processing a payment form.")
@allure.severity(allure.severity_level.BLOCKER)
@allure.link("https://www.enuygun.com", name="Enuygun Web Platform")
@allure.label("layer", "e2e")
def test_case_3_critical_path(driver, origin, destination, dep_date, ret_date):
    logger.info("--- Starting Case 3: Critical Path (End-to-End Checkout Flow) ---")
    
    passenger = MockPassenger()
    card = MockCreditCard()

    home_page = HomePage(driver)
    results_page = FlightResultPage(driver)
    passenger_page = PassengerInfoPage(driver)
    payment_page = PaymentPage(driver)
    
    
    @allure.step("Fill Passenger Information")
    def _fill_passenger_step():
        passenger_page.fill_contact_info(passenger.email, passenger.phone)
        passenger_page.fill_passenger_details(
            passenger.fname, passenger.lname, passenger.b_day, 
            passenger.b_month, passenger.b_year, passenger.id_number, passenger.gender
        )
        passenger_page.proceed_to_payment()

    with allure.step("Navigate to Enuygun and Search Flight"):
        home_page.go_to(Config.BASE_URL)
        home_page.enter_origin(origin)
        home_page.enter_destination(destination)
        home_page.select_departure_date(dep_date)
        home_page.select_return_date(ret_date)
        home_page.uncheck_hotel_offer()
        is_round_trip_search = home_page.is_round_trip()
        home_page.click_search()

    with allure.step("Select Departure and Return Flights"):
        results_page.wait_for_results_to_load()
        logger.info("Selecting the departure flight (Left Column)...")
        results_page.select_first_flight(is_return=False, is_final_flight=not is_round_trip_search)

        if is_round_trip_search:
            logger.info("Round-trip explicitly detected from Home Page. Selecting return flight (Right Column)...")
            results_page.select_first_flight(is_return=True, is_final_flight=True)
        else:
            logger.info("Single-trip detected. Proceeding directly to passenger info.")

    _fill_passenger_step()
    
    with allure.step("Verify Payment Page and Fill CC Form"):
        payment_indicator_present = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='cardNumber']"))
        )
        assert payment_indicator_present, "Failed to reach the payment screen! Card input not found."
        logger.info("Assertion Passed: Successfully reached the secure payment page.")

        payment_page.handle_membership_popup()
        payment_page.fill_credit_card(card.cc_no, card.cc_month_idx, card.cc_year_idx, card.cc_cvv)
        payment_page.submit_payment()

    logger.info("Assertion Passed: Critical path completed up to payment submission.")

    _save_success_screenshot(driver, "Case3_CriticalPath", "E2E", "Done")
    logger.info("--- Case 3 Completed Successfully ---")
    

def _validate_departure_times(departure_times: list, start_time: str, end_time: str) -> None:
    """Validate all departure times fall within the specified range and handle generic data quality."""
    assert isinstance(departure_times, list) and len(departure_times) > 0, "Departure times list cannot be empty."

    start_bound = datetime.strptime(start_time, TIME_FORMAT).time()
    end_bound = datetime.strptime(end_time, TIME_FORMAT).time()
    
    for time_str in departure_times:
        assert isinstance(time_str, str) and time_str.strip() != "", "A departure time value exists but is empty or not string."
        
        try:
            flight_time = datetime.strptime(time_str, TIME_FORMAT).time()
        except ValueError:
            pytest.fail(f"Could not parse departure time '{time_str}' with expected format {TIME_FORMAT}.")
            
        assert start_bound <= flight_time <= end_bound, (
            f"Flight departure time {time_str} is outside allowed range {start_time}-{end_time}"
        )
    
    logger.info(f"Validated {len(departure_times)} flights within {start_time}-{end_time}")


def _validate_turkish_airlines_only(airlines: list) -> None:
    """Validate all airlines are strictly Turkish Airlines variants."""
    assert isinstance(airlines, list) and len(airlines) > 0, "No airlines to validate, list is empty."

    for airline in airlines:
        assert isinstance(airline, str) and airline.strip() != "", "An airline name is unexpectedly empty."
        
        assert any(name in airline for name in TURKISH_AIRLINES_NAMES), (
            f"Expected Turkish Airlines, but found: '{airline}'"
        )
    logger.info("All flights are strictly Turkish Airlines")


def _validate_prices_ascending(prices: list) -> None:
    """Validate prices are valid numeric objects and perfectly sorted in ascending order."""
    assert isinstance(prices, list) and len(prices) > 0, "Can't validate prices sorting on an empty price list."
    
    for price in prices:
        assert isinstance(price, (int, float)), f"Expected price to be numeric, got {type(price)} with value {price}."
        assert price >= 0, f"Flight price must be realistically zero or positive. Evaluated: {price}."
        
    assert prices == sorted(prices), (
        f"Prices not strictly in ascending order.\nActual: {prices}\nExpected: {sorted(prices)}"
    )
    logger.info("Prices are numeric and correctly sorted in ascending order")


def _save_success_screenshot(driver, case_name: str, start_time: str, end_time: str) -> None:
    """Save screenshot with standardized naming."""
    time_suffix = start_time.replace(":", "") + "_" + end_time.replace(":", "")
    screenshot_name = f"{SCREENSHOT_DIR}/SUCCESS_{case_name}_{time_suffix}.png"
    driver.save_screenshot(screenshot_name)
    logger.info(f"Screenshot saved: {screenshot_name}")
