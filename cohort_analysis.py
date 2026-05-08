# ═══════════════════════════════════════════════════════════
# CONSUMER360: COHORT ANALYSIS
# Purpose: Calculate customer retention rates over time
# ═══════════════════════════════════════════════════════════

import pandas as pd
import urllib.parse
from sqlalchemy import create_engine
import warnings

warnings.filterwarnings("ignore")
print("Starting Cohort Analysis...")

# 1. Connect & Load Data
print("Loading transaction data...")
SERVER = r"DESKTOP-94L3J1Q\SQLEXPRESS"
DATABASE = "Consumer360"
params = urllib.parse.quote_plus(f"Driver={{ODBC Driver 17 for SQL Server}};Server={SERVER};Database={DATABASE};Trusted_Connection=yes;Encrypt=no;")
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

query = """
SELECT f.customer_id, f.invoice_date, c.country
FROM fact_sales f JOIN dim_customer c ON f.customer_id = c.customer_id
"""
df = pd.read_sql(query, engine)
df['invoice_date'] = pd.to_datetime(df['invoice_date'])

# 2. Assign Cohort Months
# invoice_month: when they bought, cohort_month: when they FIRST bought
df['invoice_month'] = df['invoice_date'].dt.to_period('M')
df['cohort_month'] = df.groupby('customer_id')['invoice_date'].transform('min').dt.to_period('M')

# 3. Calculate Cohort Index (Months since first purchase)
years_diff = df['invoice_month'].dt.year - df['cohort_month'].dt.year
months_diff = df['invoice_month'].dt.month - df['cohort_month'].dt.month
df['cohort_index'] = years_diff * 12 + months_diff + 1

# 4. Create Retention Matrix
print("Calculating retention rates by country...")
cohort_data = df.groupby(['country', 'cohort_month', 'cohort_index'])['customer_id'].nunique().reset_index()

# 5. Save to SQL Server
print("Saving results to database...")
cohort_data['cohort_month'] = cohort_data['cohort_month'].dt.to_timestamp() # Format for SQL
cohort_data.to_sql("cohort_analysis", engine, if_exists="replace", index=False)

print("\n[SUCCESS] Cohort Analysis Complete!")