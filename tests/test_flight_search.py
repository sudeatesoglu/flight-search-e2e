import pytest
from datetime import datetime
from loguru import logger
from pages.home_page import HomePage
from pages.flight_result_page import FlightResultPage
from core.config import Config

@pytest.mark.parametrize(
    "origin, destination, dep_date, ret_date, start_time, end_time",
    [
        ("Istanbul", "Ankara", "2026-04-15", "2026-04-20", "10:00", "18:00")
    ]
)

def test_case_1_basic_flight_search_and_time_filter(driver, origin, destination, dep_date, ret_date, start_time, end_time):
    """
    Searches for a round-trip between specified origin and destination.
    Applies a dynamic departure time filter based on start_time and end_time.
    Asserts that all returned flights fall strictly within this time range.
    """
    logger.info(f"--- Starting Case 1: {origin} to {destination} | Filter: {start_time}-{end_time} ---")
    
    # Initialize page objects
    home_page = HomePage(driver)
    results_page = FlightResultPage(driver)
    
    # Navigate and search
    home_page.go_to(Config.BASE_URL)
    home_page.search_flights(origin, destination, dep_date, ret_date)
    
    # Wait for results list and filter
    results_page.wait_for_results_to_load()
    
    # Apply dynamic time filter
    results_page.apply_departure_time_filter(start_time, end_time)
    
    # Extract departure times
    departure_times_str = results_page.get_departure_times()
    
    # Check that flight cards were actually loaded after filtering
    assert len(departure_times_str) > 0, "No flights were found after applying the time filter."
    
    logger.info(f"Validating {len(departure_times_str)} flight time(s) to ensure they are between {start_time} and {end_time}.")
    for time_str in departure_times_str:
        flight_time = datetime.strptime(time_str, "%H:%M").time()
        
        # Convert filter bounds to time objects
        start_bound = datetime.strptime(start_time, "%H:%M").time()
        end_bound = datetime.strptime(end_time, "%H:%M").time() 
        
        error_msg = f"Flight departure time {time_str} is outside the allowed range of {start_time} - {end_time}!"
        assert start_bound <= flight_time <= end_bound, error_msg
    
    # Save a screenshot for visual confirmation of the successful filter application
    screenshot_name = f"screenshots/SUCCESS_Case1_{start_time.replace(':', '')}_{end_time.replace(':', '')}.png"
    driver.save_screenshot(screenshot_name)
    logger.info(f"Success screenshot saved to {screenshot_name}")

    logger.info("--- Case 1 Completed Successfully ---")