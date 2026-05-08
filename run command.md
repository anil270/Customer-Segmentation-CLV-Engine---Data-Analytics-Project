# Run Commands & Automation Guide - Consumer360

This guide provides the complete execution flow, commands, and automation setup for the **Consumer360 Analytics Engine**.

> **Note**: Always run these commands from the project root folder.

---

## 1️⃣ Environment Setup
Before running the pipeline, ensure your Python environment is active and dependencies are installed.

```powershell
# Activate the virtual environment
.\.venv\Scripts\activate

# Install required libraries
pip install -r requirements.txt
```

---

## 2️⃣ Main Pipeline Execution (One-Click)

The most efficient way to run the entire ETL, Advanced Analytics (RFM, Market Basket, Cohorts, Predictive CLV), and Data Loading process is via the master automation script.

```powershell
# Runs the full sequence automatically
python python/automation.py
```
*Sequence executed:* `data_cleaning.py` ➔ `data_loader.py` ➔ `rfm_analysis.py` ➔ `cohort_analysis.py` ➔ `market_basket.py` ➔ `verify.py`

---

## 3️⃣ Verification & Presentation

**Live Database Check**
Instantly verify if SQL Server tables (`fact_sales`, `dim_customer`, etc.) are successfully populated:
```powershell
python python/verify.py
```

**Final Business Insights**
To view the final Executive Summary with interactive charts (matching Power BI dashboards):
- Double-click the `presentation.html` file in your browser.

---

## 4️⃣ 100% Zero-Touch Automation Setup

The project is fully automated for weekly execution without human intervention.

### Part A: Python Pipeline Automation (Local Backend)
To schedule the Python pipeline to run automatically **every Sunday at 11:00 PM** via Windows Task Scheduler:
```powershell
python python/schedule_task.py
```

### Part B: Power BI Cloud Automation (Frontend)
To ensure the Power BI Dashboards automatically reflect the new data fetched by Python:
1. Install **Power BI Personal Data Gateway** on this machine.
2. Publish your report to Power BI Service (`app.powerbi.com`).
3. In Dataset Settings > Gateway Connection, map your local SQL credentials (Windows Authentication).
4. Set **Scheduled Refresh** for **Every Monday at 01:00 AM**.

---

## 5️⃣ Manual Script Execution (Optional)
If you need to run specific modules individually for debugging:

| Task | Command |
|---|---|
| **Clean & Format Data** | `python python/data_cleaning.py` |
| **Raw Data Extraction to SQL** | `python python/data_loader.py` |
| **RFM & Predictive CLV** | `python python/rfm_analysis.py` |
| **Cohort Retention Data**| `python python/cohort_analysis.py` |
| **Market Basket Rules** | `python python/market_basket.py` |

---

## 6️⃣ Database Reset
To reset the entire database structure from scratch (Warning: Deletes existing data):
1. Open **SSMS** (SQL Server Management Studio).
2. Open `sql/schema.sql` and click **Execute**.

---
*Status: LIVE & PRODUCTION READY 🚀*
