import pytest
from datetime import datetime
from loguru import logger
from pages.home_page import HomePage
from pages.flight_result_page import FlightResultPage
from core.config import Config

@pytest.mark.parametrize(
    "origin, destination, dep_date, ret_date",
    [
        ("Istanbul", "Ankara", "2026-04-15", "2026-04-20")
    ]
)

def test_case_1_basic_flight_search_and_time_filter(driver, origin, destination, dep_date, ret_date):
    """
    Searches for a round-trip between Istanbul and Ankara.
    Applies a 10:00 AM to 6:00 PM departure filter.
    Asserts that all returned flights fall strictly within this 10:00 - 18:00 range.
    """
    logger.info(f"--- Starting Case 1: {origin} to {destination} ---")
    
    # Initialize page objects
    home_page = HomePage(driver)
    results_page = FlightResultPage(driver)
    
    # Navigate and search
    home_page.go_to(Config.BASE_URL)
    home_page.search_flights(origin, destination, dep_date, ret_date)
    
    # Wait for results list and filter
    results_page.wait_for_results_to_load()
    results_page.apply_departure_time_filter()
    
    # Extract departure times
    departure_times_str = results_page.get_departure_times()
    
    # Check that flight cards were actually loaded after filtering
    assert len(departure_times_str) > 0, "No flights were found after applying the time filter."
    
    logger.info(f"Validating {len(departure_times_str)} flight time(s) to ensure they are between 10:00 and 18:00.")
    for time_str in departure_times_str:
        flight_time = datetime.strptime(time_str, "%H:%M").time()
        
        start_bound = datetime.strptime("10:00", "%H:%M").time()
        end_bound = datetime.strptime("18:00", "%H:%M").time() 
        
        error_msg = f"Flight departure time {time_str} is outside the allowed range of 10:00 - 18:00!"
        assert start_bound <= flight_time <= end_bound, error_msg

    logger.info("--- Case 1 Completed Successfully ---")