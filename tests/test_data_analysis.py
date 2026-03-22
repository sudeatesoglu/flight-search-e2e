import pytest
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

# Constants
DATA_DIR = "data"
CSV_FILE_PATH = f"{DATA_DIR}/nicosia_flights.csv"
TOP_FLIGHTS_CSV = f"{DATA_DIR}/top_cost_effective_flights.csv"
PRICES_CHART_PATH = f"{DATA_DIR}/airline_prices.png"
HEATMAP_CHART_PATH = f"{DATA_DIR}/price_heatmap.png"

@pytest.mark.parametrize(
    "origin, destination, dep_date, ret_date",
    [
        ("Istanbul", "Lefkosa", "2026-04-15", "2026-04-20")
    ]
)
def test_case_4_web_scraping_and_csv_export(driver, origin, destination, dep_date, ret_date):
    """
    Performs a search and scrapes all flight data into a CSV file.
    """
    logger.info(f"--- Starting Case 4: Web Scraping ({origin} to {destination}) ---")
    
    home_page = HomePage(driver)
    results_page = FlightResultPage(driver)
    
    home_page.go_to(Config.BASE_URL)
    home_page.search_flights(origin, destination, dep_date, ret_date)
    results_page.wait_for_results_to_load()
    
    flight_data = results_page.extract_all_flight_data()
    assert len(flight_data) > 0, "No flight data could be scraped!"
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    keys = flight_data[0].keys()
    with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(flight_data)
        
    logger.info(f"Successfully saved {len(flight_data)} flight records to {CSV_FILE_PATH}")
    assert os.path.exists(CSV_FILE_PATH), "CSV file was not created successfully."
    logger.info("--- Case 4 (Scraping) Completed Successfully ---")


def test_case_5_flight_data_analysis():
    """
    Reads the scraped CSV data, performs data analysis, 
    and generates visual reports and cost-effectiveness scores.
    """
    logger.info("--- Starting Case 5: Data Analysis and Visualization ---")
    
    if not os.path.exists(CSV_FILE_PATH):
        pytest.skip(f"Skipping analysis: '{CSV_FILE_PATH}' not found. Ensure Case 4 runs first.")

    df = pd.read_csv(CSV_FILE_PATH)
    assert not df.empty, "The CSV file is empty, cannot perform analysis."

    logger.info("Generating Minimum, Average, and Maximum Prices chart...")
    agg_df = df.groupby('Airline')['Price'].agg(['min', 'max', 'mean']).reset_index()

    plt.figure(figsize=(10, 6))
    x = np.arange(len(agg_df))
    width = 0.25 

    plt.bar(x - width, agg_df['min'], width, label='Min Price', color='#7eb0d5')
    plt.bar(x, agg_df['mean'], width, label='Avg Price', color='#b2e061')
    plt.bar(x + width, agg_df['max'], width, label='Max Price', color='#bd7ebe')

    plt.xlabel('Airline', fontsize=12)
    plt.ylabel('Price (TRY)', fontsize=12)
    plt.title('Minimum, Average, and Maximum Prices by Airline', fontsize=14)
    plt.xticks(x, agg_df['Airline'])
    plt.legend()
    plt.tight_layout()

    plt.savefig(PRICES_CHART_PATH)
    logger.info(f"Saved prices chart to {PRICES_CHART_PATH}")
    plt.close()

    logger.info("Generating Heat Map for price distribution by time slot...")
    df['Hour'] = pd.to_datetime(df['Departure Time'], format='%H:%M').dt.hour
    bins = [-1, 5, 11, 17, 23]
    labels = ['Night (00-05)', 'Morning (06-11)', 'Afternoon (12-17)', 'Evening (18-23)']
    df['Time Slot'] = pd.cut(df['Hour'], bins=bins, labels=labels, right=True)

    heatmap_data = df.pivot_table(values='Price', index='Airline', columns='Time Slot', aggfunc='mean', observed=False)

    plt.figure(figsize=(9, 6))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlOrRd", cbar_kws={'label': 'Average Price (TRY)'})
    plt.title('Average Flight Price by Airline and Time Slot', fontsize=14)
    plt.tight_layout()

    plt.savefig(HEATMAP_CHART_PATH)
    logger.info(f"Saved heatmap chart to {HEATMAP_CHART_PATH}")
    plt.close()

    logger.info("Calculating cost-effectiveness scores...")
    
    def parse_duration(d_str):
        parts = str(d_str).split(' ')
        h, m = 0, 0
        for part in parts:
            if 'sa' in part:
                h = int(part.replace('sa', ''))
            elif 'dk' in part:
                m = int(part.replace('dk', ''))
        return h * 60 + m

    df['Duration_min'] = df['Duration'].apply(parse_duration)

    price_range = df['Price'].max() - df['Price'].min()
    dur_range = df['Duration_min'].max() - df['Duration_min'].min()
    
    df['Norm_Price'] = (df['Price'] - df['Price'].min()) / price_range if price_range > 0 else 0
    df['Norm_Duration'] = (df['Duration_min'] - df['Duration_min'].min()) / dur_range if dur_range > 0 else 0

    df['Score'] = (df['Norm_Price'] * 0.7) + (df['Norm_Duration'] * 0.3)
    best_flights = df.sort_values('Score').head(5)

    best_flights[['Departure Time', 'Arrival Time', 'Airline', 'Price', 'Transit', 'Duration', 'Score']].to_csv(TOP_FLIGHTS_CSV, index=False)
    
    logger.info(f"Saved top cost-effective flights to {TOP_FLIGHTS_CSV}")
    logger.info("--- Top 5 Most Cost-Effective Flights ---")
    
    for index, row in best_flights.iterrows():
        logger.info(f"Airline: {row['Airline']} | Dep: {row['Departure Time']} | Price: {row['Price']} TRY | Dur: {row['Duration']} | Score: {row['Score']:.3f}")

    assert os.path.exists(PRICES_CHART_PATH) and os.path.exists(HEATMAP_CHART_PATH), "Charts were not generated successfully."
    logger.info("--- Case 5 (Analysis) Completed Successfully ---")
    