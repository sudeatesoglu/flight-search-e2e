# Flight Search E2E Test & Data Analysis Pipeline

This repository contains a comprehensive End-to-End (E2E) Test Automation and Data Analysis Framework designed for a flight search platform. It goes beyond traditional UI testing by incorporating web scraping, dynamic CLI parameterization, and cost-effectiveness data visualization.

Built with **Selenium**, **Pytest**, and **Pandas**, it follows strict Page Object Model (POM), Object-Oriented Programming (OOP), and Clean Code principles (e.g., Dataclasses for mock data).

## Tech Stack

- **Language:** Python 3.14+
- **Test Framework:** Pytest (with CLI customization)
- **Browser Automation:** Selenium WebDriver 4.41.0+
- **Data Analysis & Vis:** Pandas, Matplotlib, Seaborn, NumPy
- **Reporting:** Allure Reports
- **Logging:** Loguru
- **Environment Management:** Python-dotenv
- **Package Manager:** `uv` (recommended) or `pip`

## Key Features

- **Dynamic CLI Execution:** Run tests for any route and date directly from the terminal (e.g., `--origin Izmir --destination Ankara --dep-date 2026-06-10`).
- **Smart Calendar Navigation:** Includes a dynamic loop that automatically pages through calendar months until the target date is injected into the DOM.
- **Data Scraping & Analysis:** Extracts flight prices, durations, and airlines into CSVs. Calculates a normalized "Cost-Effectiveness Score" (70% Price, 30% Duration).
- **High-Res Visualizations:** Generates Seaborn heatmaps (Price by Time Slot) and Matplotlib grouped bar charts (Min/Avg/Max prices).
- **Master Comparison Log:** Appends summary metrics of every test run into a central `flight_comparison_master.csv` to track price changes across different routes/dates.
- **Separation of Concerns:** Uses Python `@dataclass` to isolate mock passenger and payment data from the core test logic.
- **Automated Screenshots & Allure:** Captures visual evidence on failure and compiles comprehensive HTML reports.

## Prerequisites

- Python 3.14+
- Chrome and/or Firefox browsers installed
- **Allure Commandline** (for HTML reports):
  - macOS: `brew install allure`
  - Windows: `scoop install allure` or `npm install -g allure-commandline`

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sudeatesoglu/flight-search-e2e.git](https://github.com/sudeatesoglu/flight-search-e2e.git)
   cd flight-search-e2e
   ```

2. **Set up the virtual environment:**
   Using `uv` (Fastest):
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r pyproject.toml
   ```

3. **Environment Setup:**
   ```bash
   cp .env.example .env
   # Edit .env to set your BASE_URL, BROWSER, etc.
   ```

## Running the Tests (CLI Usage)

The framework is configured via `pyproject.toml` to always output live logs (`-v -s`). You can override the default search parameters using custom CLI flags.

**Run the full suite with custom route and dates:**
```bash
pytest tests/ --origin Antalya --destination Istanbul --dep-date 2026-05-10 --ret-date 2026-05-15 --start-time 08:00 --end-time 12:00
```

**Run ONLY the Data Analysis & Visualization scenario:**
```bash
pytest tests/test_data_analysis.py --origin Izmir --destination Ankara --dep-date 2026-06-01
```

**Run the Critical Path (Checkout) with Allure Reporting:**
```bash
pytest tests/test_flight_search.py -k "critical_path" --alluredir=allure-results
```

## Outputs & Reports

### 1. Live Execution Logs
Powered by Loguru, the framework provides real-time, colorful console output and saves history to `test_execution.log`.
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
