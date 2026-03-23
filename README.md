# Flight Search E2E Test & Data Analysis Pipeline

This repository contains a comprehensive End-to-End (E2E) Test Automation and Data Analysis Framework designed for a flight search platform (Enuygun.com). It goes beyond traditional UI testing by incorporating web scraping, dynamic CLI parameterization, and cost-effectiveness data visualization.

Built with **Selenium**, **Pytest**, and **Pandas**, it follows strict Page Object Model (POM), Object-Oriented Programming (OOP), and Clean Code principles.

## Case Study Requirements & Implementations

This project was built to satisfy the following core requirements:

1. **Case 1 (Basic Flight Search & Time Filter):** Implemented in `test_case_1_departure_time_filtering`. Validates UI filtering for a parameterized route, date, and 10:00 AM - 6:00 PM time blocks.
2. **Case 2 (Price Sorting for Turkish Airlines):** Implemented in `test_case_2_turkish_airlines_price_sorting`. Ensures UI applies strict filters for Turkish Airlines and validates that prices are strictly ascending.
3. **Case 3 (Critical Path Testing):** Implemented in `test_case_3_critical_path`. Navigates through search, flight selections (departure and return), passenger form completion, and halts at the secure credit card iframe injection to validate the complete booking funnel.
4. **Case 4 (Analysis and Categorization):** Implemented in `test_data_analysis.py`. Scrapes all flights for the route, saves to a dynamic CSV, calculates cost-effectiveness scores, and generates Seaborn heatmaps (Price by Time Slot) and Matplotlib bar charts (Min/Avg/Max prices).

## Technical Stack & Architecture

- **Language:** Python 3.14+
- **Test Framework:** Pytest (with CLI customization)
- **Browser Automation:** Selenium WebDriver 4.41.0+
- **Design Pattern:** Page Object Model (POM) & Object-Oriented Programming (OOP)
- **Data Analysis & Vis:** Pandas, Matplotlib, Seaborn
- **Reporting:** Allure Reports (with Epic/Feature/Story decorators and automatic screenshot formatting)
- **Logging:** Loguru (real-time console and file logging)
- **Environment Management:** Python-dotenv
- **Cross-Browser Testing:** Configurable for **Chrome** and **Firefox**

## Prerequisites & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sudeatesoglu/flight-search-e2e.git
   cd flight-search-e2e
   ```

2. **Set up the virtual environment:**
   Using `uv` (Fastest):
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. **Environment Setup:**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and configure your settings.
   To switch browsers, simply change `BROWSER` in the `.env` file:
   ```env
   BROWSER=chrome   # or BROWSER=firefox
   HEADLESS=true
   ```

## Running the Tests (CLI Usage)

The framework is strictly built around dynamic data injection to fulfill the requirement: *"Cities should be parameterized"*. 

The default fallback values are configured in `conftest.py` as:
- Origin: `Istanbul`
- Destination: `Lefkosa`

To run the cases exactly as requested in the Case Study (e.g., Istanbul to Ankara for Cases 1 & 2), you **must provide the explicit CLI arguments**. Tests are configured to run locally across both Chrome and Firefox based on `.env`.

**Run the full suite with explicit Case Study parameters:**
```bash
uv run pytest tests/ --origin Istanbul --destination Ankara --dep-date 2026-05-10 --ret-date 2026-05-15 --start-time 10:00 --end-time 18:00
```

## Running the Tests Individually

You can run each case individually using the pytest `-k` flag to specify the exact function name. We pass the explicit `--origin` and `--destination` parameters required for each scenario as per the test document.

**Case 1: Basic Flight Search and Time Filter**
Validates that flights from Istanbul to Ankara are correctly filtered between 10:00 AM and 6:00 PM.
```bash
uv run pytest tests/test_flight_search.py -k "test_case_1_basic_flight_search_and_time_filter" --origin Istanbul --destination Ankara --start-time 10:00 --end-time 18:00
```

**Case 2: Price Sorting for Turkish Airlines**
Validates that Turkish Airlines flights (Istanbul -> Ankara) are correctly filtered and prices are sorted in strict ascending order.
```bash
uv run pytest tests/test_flight_search.py -k "test_case_2_turkish_airlines_price_sorting" --origin Istanbul --destination Ankara
```

**Case 3: Critical User Path (End-to-End Checkout)**
Executes the full booking journey from search to the credit card payment step.
```bash
uv run pytest tests/test_flight_search.py -k "test_case_3_critical_path"
```

**Case 4: Data Scraping, Analysis, and Categorization**
Scrapes flight results (Istanbul -> Nicosia route as requested) into a CSV, computes cost-effectiveness, and generates visualization charts (Heatmap & Bar charts).
```bash
uv run pytest tests/test_data_analysis.py --origin Istanbul --destination Lefkosa
```

## Outputs & Reports

### 1. Allure Reports (Screenshots on Failure)
The framework uses Allure for comprehensive test reporting, including `@allure.step` definitions, `@allure.epic` categorization, and **automatic screenshot captures on test failures**. Data Analysis charts (PNG) and Pandas datasets (CSV) are also automatically attached to the Allure report!

To generate and view the report:
```bash
# Run tests and save Allure data to the allure-results folder
uv run pytest tests/ --alluredir=allure-results

# Serve the report locally
allure serve allure-results
```

*(Note: Requires Allure Commandline to be installed on your machine. e.g., `brew install allure`)*

### 2. Live Execution Logs
Powered by Loguru, the framework provides real-time, colorful console output and saves execution history to `test_execution.log`.

```text
2026-03-23 10:41:42.501 | INFO     | pages.home_page:_select_date_from_calendar:120 - Searching for Date: 2026-05-10 in the calendar...
2026-03-23 10:41:43.564 | INFO     | pages.base_page:click_element_with_js:85 - Successfully clicked element with JS: ('css selector', "[data-testid$='month-forward-button']")
2026-03-23 10:41:43.585 | INFO     | pages.home_page:_select_date_from_calendar:128 - Date 2026-05-10 selected successfully.
2026-03-23 10:42:35.449 | INFO     | pages.flight_result_page:apply_departure_time_filter:63 - Applying Departure Time filter: 08:00 - 12:00 (480 - 720 mins).
2026-03-23 10:42:42.707 | INFO     | tests.test_flight_search:_validate_departure_times:141 - Validated 11 flights within 08:00-12:00
2026-03-23 10:42:43.275 | INFO     | tests.test_flight_search:test_case_1_basic_flight_search_and_time_filter:47 - Case 1 completed successfully
```

### 2. Generated Data & Visualizations (Case 4)
Running the analysis test automatically generates files in the `data/` directory:
- `*_raw_flights.csv`: Unfiltered, scraped DOM data.
- `*_top_cost_effective.csv`: Top 5 flights based on the algorithm score.
- `*_airline_prices.png`: High-res Bar Chart with direct value annotations.
- `*_price_heatmap.png`: High-res Seaborn Heatmap segmented by time of day.
- `flight_comparison_master.csv`: A continuous log appending summary stats of every executed test for cross-comparison.

### 3. Allure Reports
All test results, including attached screenshots and logs, are exported to the `allure-results` directory.

If a test fails, a timestamped screenshot is captured in the `screenshots/` directory (e.g., `test_case_2_turkish_airlines_20260323_103409.png`) and attached to the Allure report.

**To generate and serve the Allure HTML report:**
```bash
# Serve the report in your default browser automatically
allure serve allure-results
```

*Note: If you encounter an error like `command not found: allure`, make sure you have installed Allure Commandline globally on your OS (macOS: `brew install allure`).*

## Project Structure

```text
flight-search-e2e/
├── core/
│   └── config.py          # Environment & configuration loader
├── data/                  # Test data files (.json, .csv, etc.)
├── pages/                 # Page Object Model (POM) classes
│   ├── base_page.py       # Core wrapper for WebDriver actions
│   ├── home_page.py       # Home page interactions
│   ├── flight_result_page.py
│   ├── passenger_info_page.py
│   ├── payment_page.py
│   └── locators.py        # Centralized UI locators
├── screenshots/           # Auto-generated failure screenshots
├── tests/                 # Pytest test cases
│   ├── test_data_analysis.py
│   └── test_flight_search.py
├── conftest.py            # Pytest fixtures, hook configs, & WebDriver setup
├── pyproject.toml         # Project dependencies and configurations
└── README.md              # Project documentation
```
