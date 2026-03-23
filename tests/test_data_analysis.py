import pytest
import allure
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from loguru import logger

from pages.home_page import HomePage
from pages.flight_result_page import FlightResultPage
from core.config import Config

DATA_DIR = "data"

class FlightDataAnalyzer:
    """Helper class to handle data manipulation, scoring, and beautiful visualizations."""
    
    def __init__(self, csv_path: str, report_prefix: str):
        self.df = pd.read_csv(csv_path)
        self.report_prefix = report_prefix
        
        sns.set_theme(style="whitegrid", palette="muted")
        
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def generate_price_summary_chart(self) -> str:
        """Generates and saves a bar chart of min, max, and avg prices."""
        logger.info("Generating Minimum, Average, and Maximum Prices chart...")
        agg_df = self.df.groupby('Airline')['Price'].agg(['min', 'max', 'mean']).reset_index()

        plt.figure(figsize=(10, 6))
        x = np.arange(len(agg_df))
        width = 0.25 

        plt.bar(x - width, agg_df['min'], width, label='Min Price', color='#4C72B0')
        plt.bar(x, agg_df['mean'], width, label='Avg Price', color='#55A868')
        plt.bar(x + width, agg_df['max'], width, label='Max Price', color='#C44E52')

        plt.xlabel('Airline', fontsize=12, fontweight='bold')
        plt.ylabel('Price (TRY)', fontsize=12, fontweight='bold')
        plt.title(f'Price Distribution by Airline\n({self.report_prefix})', fontsize=14, fontweight='bold')
        plt.xticks(x, agg_df['Airline'], rotation=15)
        plt.legend()
        plt.tight_layout()

        output_path = f"{DATA_DIR}/{self.report_prefix}_airline_prices.png"
        plt.savefig(output_path, dpi=300)
        plt.close()
        return output_path

    def generate_time_slot_heatmap(self) -> str:
        """Generates and saves a heatmap of prices by time slot."""
        logger.info("Generating Heat Map for price distribution by time slot...")
        
        self.df['Hour'] = pd.to_datetime(self.df['Departure Time'], format='%H:%M').dt.hour
        bins = [-1, 5, 11, 17, 23]
        labels = ['Night (00-05)', 'Morning (06-11)', 'Afternoon (12-17)', 'Evening (18-23)']
        self.df['Time Slot'] = pd.cut(self.df['Hour'], bins=bins, labels=labels, right=True)

        heatmap_data = self.df.pivot_table(values='Price', index='Airline', columns='Time Slot', aggfunc='mean', observed=False)

        plt.figure(figsize=(10, 6))
        sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu", cbar_kws={'label': 'Average Price (TRY)'})
        plt.title(f'Average Flight Price by Airline and Time Slot\n({self.report_prefix})', fontsize=14, fontweight='bold')
        plt.tight_layout()

        output_path = f"{DATA_DIR}/{self.report_prefix}_price_heatmap.png"
        plt.savefig(output_path, dpi=300)
        plt.close()
        return output_path

    @staticmethod
    def parse_duration(d_str: str) -> int:
        """Helper to convert duration strings like '1sa 30dk' to total minutes."""
        parts = str(d_str).split(' ')
        h, m = 0, 0
        for part in parts:
            if 'sa' in part:
                h = int(part.replace('sa', ''))
            elif 'dk' in part:
                m = int(part.replace('dk', ''))
        return h * 60 + m

    def calculate_cost_effectiveness(self) -> str:
        """Calculates normalized score (70% Price, 30% Duration) and saves top 5."""
        logger.info("Calculating cost-effectiveness scores...")
        self.df['Duration_min'] = self.df['Duration'].apply(self.parse_duration)

        # Min-Max Normalization
        price_range = self.df['Price'].max() - self.df['Price'].min()
        dur_range = self.df['Duration_min'].max() - self.df['Duration_min'].min()
        
        self.df['Norm_Price'] = (self.df['Price'] - self.df['Price'].min()) / price_range if price_range > 0 else 0
        self.df['Norm_Duration'] = (self.df['Duration_min'] - self.df['Duration_min'].min()) / dur_range if dur_range > 0 else 0

        self.df['Score'] = (self.df['Norm_Price'] * 0.7) + (self.df['Norm_Duration'] * 0.3)
        best_flights = self.df.sort_values('Score').head(5)

        output_path = f"{DATA_DIR}/{self.report_prefix}_top_cost_effective.csv"
        best_flights[['Departure Time', 'Arrival Time', 'Airline', 'Price', 'Transit', 'Duration', 'Score']].to_csv(output_path, index=False)
        
        logger.info(f"--- Top 5 Most Cost-Effective Flights ({self.report_prefix}) ---")
        for _, row in best_flights.iterrows():
            logger.info(f"Airline: {row['Airline']} | Dep: {row['Departure Time']} | Price: {row['Price']} TRY | Dur: {row['Duration']} | Score: {row['Score']:.3f}")
            
        return output_path


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
        assert len(flight_data) > 0, "No flight data could be scraped!"
        
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
    