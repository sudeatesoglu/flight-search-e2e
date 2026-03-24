import pytest
import allure
import csv
import os
from loguru import logger

from pages.home_page import HomePage
from pages.flight_result_page import FlightResultPage
from core.config import Config
from utils.data_analyzer import FlightDataAnalyzer, DATA_DIR

@allure.epic("Data Analysis and Machine Learning")
@allure.feature("Flight Price Mining & Analysis")
@allure.story("Data categorization and visual report generation")
@allure.title("Test Case 4: Flight Results Scraping and Scoring ({origin} -> {destination})")
@allure.description("Scrape search results to generate a raw CSV dataset. Analyze the dataset to compute cost-effectiveness scores, plot an airline price summary, and create a time-slot average price heatmap.")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("layer", "e2e_data")
def test_case_4_analysis_and_categorization(driver, origin, destination, dep_date, ret_date):
    """
    End-to-end test that satisfies Case 4: Search, Scrape, Analyze, and Categorize.
    Dynamically generates files based on the route to allow comparison.
    """
    report_prefix = f"{origin}_{destination}_{dep_date}".lower().replace(" ", "_")
    csv_file_path = f"{DATA_DIR}/{report_prefix}_raw_flights.csv"
    
    logger.info(f"--- Starting Case 4: Analysis and Categorization for {origin} to {destination} ---")
    
    with allure.step("Navigate to Enuygun and Search for Flights (Scraping Task)"):
        home_page = HomePage(driver)
        results_page = FlightResultPage(driver)
        home_page.go_to(Config.BASE_URL)
        home_page.search_flights(origin, destination, dep_date, ret_date)
        results_page.wait_for_results_to_load()
        
    with allure.step("Extract All Visible Flight Data"):
        flight_data = results_page.extract_all_flight_data()
        assert len(flight_data) > 0, "No flight data could be scraped from the page!"
        
        # Enhanced Data Quality Assertions
        for index, flight in enumerate(flight_data):
            # Assert Airline Name is valid
            assert flight.get("Airline"), f"Row {index}: Airline name is empty or missing."
            assert isinstance(flight["Airline"], str), f"Row {index}: Airline name should be a string."

            # Assert Price is present and represents a numeric concept
            assert flight.get("Price") is not None, f"Row {index}: Price is missing."
            try:
                price_val = float(flight["Price"])
                assert price_val > 0, f"Row {index}: Price must be greater than zero, got {price_val}."
            except ValueError:
                pytest.fail(f"Row {index}: Price '{flight['Price']}' could not be converted to a numeric value.")
                
            # Assert Time strings are not totally empty
            assert flight.get("Departure Time"), f"Row {index}: Departure time is empty."
            assert flight.get("Arrival Time"), f"Row {index}: Arrival time is empty."
            
            # Assert Duration is filled
            assert flight.get("Duration"), f"Row {index}: Flight duration is empty."
        
    with allure.step(f"Save Raw Data to {csv_file_path}"):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        keys = flight_data[0].keys()
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(flight_data)
        logger.info(f"Data extraction complete. Raw data saved to {csv_file_path}")

    # Analyzing Phase
    with allure.step(f"Analyze Data from {csv_file_path}"):
        analyzer = FlightDataAnalyzer(csv_file_path, report_prefix)
        price_chart_path = analyzer.generate_price_summary_chart()
        allure.attach.file(price_chart_path, "Price Summary Bar Chart", allure.attachment_type.PNG)
        
        heatmap_path = analyzer.generate_time_slot_heatmap()
        allure.attach.file(heatmap_path, "Price vs Time Heatmap", allure.attachment_type.PNG)
        
        top_flights_path = analyzer.calculate_cost_effectiveness()
        allure.attach.file(top_flights_path, "Top 5 Cost-Effective Flights CSV", allure.attachment_type.CSV)
    
    # Assertions
    assert os.path.exists(price_chart_path), "Price summary chart was not created."
    assert os.path.exists(heatmap_path), "Time slot heatmap was not created."
    assert os.path.exists(top_flights_path), "Top cost-effective flights CSV was not created."
    
    logger.info("--- Case 4 Completed Successfully ---")
    