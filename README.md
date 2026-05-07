#  Consumer360 - Retail Analytics & Customer Intelligence

## Project Overview
Consumer360 is an automated end-to-end data pipeline designed for e-commerce retailers. It transforms raw transaction data into professional business insights through RFM Customer Segmentation and Market Basket Analysis.

### Key Features
1. **Automated ETL**: Cleans raw Excel data and loads it into a SQL Server Star Schema.
2. **RFM Segmentation**: Categorizes customers (Champions, Loyal, At-Risk) using Python.
3. **Predictive CLV**: Uses the `lifetimes` library to predict future customer value.
4. **Cohort Analysis**: Tracks customer retention rates grouped by first purchase month.
5. **Market Basket Analysis**: Identifies product associations to drive cross-selling.
6. **Live Verification**: Instant health-check script to confirm data integrity in SQL Server.
7. **Smart Scheduling**: Automatically updates the entire database every Sunday at 11 PM.

---

##  Tech Stack
| Component | Technology |
|---|---|
| **Programming** | Python (Pandas, MLxtend, SQLAlchemy) |
| **Database** | SQL Server (Star Schema Architecture) |
| **Automation** | Windows Task Scheduler |
| **Environment** | Virtual Environment (.venv) |

---

##  How to Run

### 1. The "One-Click" Full Pipeline (Recommended)
This runs the entire process: Cleaning -> Loading -> RFM -> MBA -> Verification.
```bash
python python/automation.py
```

### 2. Manual Health Check
To verify if your SQL Server tables have fresh data:
```bash
python python/verify.py
```

### 3. Setup Automation (Scheduling)
To register the pipeline to run automatically every Sunday at 11 PM:
```bash
python python/schedule_task.py
```

---

##  Project Structure
```text
Consumer360/
├── data/
│   ├── raw/             # Original Excel dataset
│   └── processed/       # Cleaned CSV outputs
├── sql/
│   └── schema.sql       # SQL Server Table Structures
├── python/
│   ├── automation.py    # Master Orchestrator (Main Entry Point)
│   ├── data_cleaning.py # ETL & Data Transformation
│   ├── rfm_analysis.py  # Customer Segmentation Logic
│   ├── market_basket.py # Product Association Logic
│   ├── verify.py        # Live Database Health Check
│   └── schedule_task.py # Sunday Night Automation Setup
├── requirements.txt     # Essential Libraries
└── README.md            # Project Documentation
```
