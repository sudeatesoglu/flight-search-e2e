import pytest
from datetime import datetime
from loguru import logger

# Constants
TIME_FORMAT = "%H:%M"
SCREENSHOT_DIR = "screenshots"
TURKISH_AIRLINES_NAMES = ("Türk Hava Yolları", "THY")

def validate_departure_times(departure_times: list, start_time: str, end_time: str) -> None:
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


def validate_turkish_airlines_only(airlines: list) -> None:
    """Validate all airlines are strictly Turkish Airlines variants."""
    assert isinstance(airlines, list) and len(airlines) > 0, "No airlines to validate, list is empty."

    for airline in airlines:
        assert isinstance(airline, str) and airline.strip() != "", "An airline name is unexpectedly empty."
        
        assert any(name in airline for name in TURKISH_AIRLINES_NAMES), (
            f"Expected Turkish Airlines, but found: '{airline}'"
        )
    logger.info("All flights are strictly Turkish Airlines")


def validate_prices_ascending(prices: list) -> None:
    """Validate prices are valid numeric objects and perfectly sorted in ascending order."""
    assert isinstance(prices, list) and len(prices) > 0, "Can't validate prices sorting on an empty price list."
    
    for price in prices:
        assert isinstance(price, (int, float)), f"Expected price to be numeric, got {type(price)} with value {price}."
        assert price >= 0, f"Flight price must be realistically zero or positive. Evaluated: {price}."
        
    assert prices == sorted(prices), (
        f"Prices not strictly in ascending order.\nActual: {prices}\nExpected: {sorted(prices)}"
    )
    logger.info("Prices are numeric and correctly sorted in ascending order")


def save_success_screenshot(driver, case_name: str, start_time: str, end_time: str) -> None:
    """Save screenshot with standardized naming."""
    time_suffix = start_time.replace(":", "") + "_" + end_time.replace(":", "")
    screenshot_name = f"{SCREENSHOT_DIR}/SUCCESS_{case_name}_{time_suffix}.png"
    driver.save_screenshot(screenshot_name)
    logger.info(f"Screenshot saved: {screenshot_name}")
