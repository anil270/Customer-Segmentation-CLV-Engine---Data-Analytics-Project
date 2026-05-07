# ═══════════════════════════════════════════════════════════
# CONSUMER360: DATA CLEANING
# Purpose: Clean raw data and save to a CSV file & Database
# ═══════════════════════════════════════════════════════════

import pandas as pd
import data_loader

print("Starting data cleaning process...")
df = pd.read_excel('data/raw/online_retail_II.xlsx')
print(f"Original rows: {len(df)}")

# 1. Standardize Columns
df.columns = df.columns.str.lower().str.replace(' ', '_')
df.rename(columns={'invoice_date': 'invoicedate'}, inplace=True)

# 2. Clean Data (Remove missing IDs, Cancellations, and negative/bad values)
df = df.dropna(subset=['customer_id'])
df = df[~df['invoice'].astype(str).str.startswith('C')]
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df = df[(df['quantity'] > 0) & (df['price'] > 0)].copy()

# 3. Format Types & Add Business Features
df['customer_id'] = df['customer_id'].astype(int)
df['invoicedate'] = pd.to_datetime(df['invoicedate'])
df['total_amount'] = df['quantity'] * df['price']
df['date_only'] = df['invoicedate'].dt.date

print(f"Data cleaned! Remaining rows: {len(df)}")

# 4. Save to CSV and Database
df.to_csv('data/processed/cleaned_retail.csv', index=False)
try:
    print("Uploading to SQL Server...")
    data_loader.load_to_sql_server(df)
except Exception as e:
    print(f"Error uploading: {e}")

print("Data Cleaning Complete!")
