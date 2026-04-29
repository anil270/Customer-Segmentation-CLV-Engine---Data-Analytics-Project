# Consumer360 - Customer Segmentation & CLV Engine

## Project Overview

**Consumer360** is a customer segmentation and lifetime value analysis system for e-commerce retailers. It automates the process of transforming raw transaction data into actionable business insights.

### Solution Architecture
Built an end-to-end automated analytics pipeline that:
1. **ETL**: Cleans, validates, and loads transaction data into SQL Server.
2. **RFM Modeling**: Segments customers into Champions, Loyal, At-Risk, etc.
3. **Market Basket Analysis**: Identifies product association rules for cross-selling.
4. **Insights Dashboard**: Provides a professional HTML presentation of live KPIs.
5. **Automation**: Fully scheduled weekly updates.

## Tech Stack

| Component | Technology |
|---|---|
| Data Source | Excel (Online Retail II dataset) |
| Pipeline Engine | Python (Pandas, MLxtend, PyODBC) |
| Database | SQL Server (Star Schema) |
| Visualization | Power BI / Interactive HTML Deck |
| Automation | Python (Windows Task Scheduler integration) |

## How to Run

### 1. Automated Execution (Recommended)
The project is scheduled to run every **Sunday at 11:00 PM** via Windows Task Scheduler.
*   **To Manage Schedule**: Run `python python/schedule_task.py` to re-register or update the schedule.

### 2. Manual Execution Options

#### Option A: Full Master Pipeline (Recommended)
Run everything in one go (ETL + RFM + MBA):
*   `python python/automation.py`

#### Option B: Modular Execution (Step-by-Step)
If you want to run specific components individually:
*   **Step 1 (ETL)**: `python python/data_cleaning.py`
*   **Step 2 (RFM)**: `python python/rfm_analysis.py`
*   **Step 3 (MBA)**: `python python/market_basket.py`

## Viewing Results
*   **Interactive Insights**: Open `presentation.html` in any web browser.
*   **SQL Database**: Connect to SQL Server and explore the `Consumer360` database.
*   **Processed Files**: CSV outputs are stored in `data/processed/`.

## Project Structure
```text
Consumer360/
├── data/
│   ├── raw/             # Original Excel dataset
│   └── processed/       # Cleaned CSVs (Retail, RFM, MBA)
├── logs/                 # Pipeline execution logs
├── python/
│   ├── automation.py    # Master script (Pipeline)
│   ├── data_cleaning.py # Modular ETL script
│   ├── rfm_analysis.py  # Modular RFM model
│   ├── market_basket.py # Modular MBA script
│   └── schedule_task.py # Scheduling manager
├── presentation.html    # Interactive Business Insights deck
└── README.md            # Documentation
```