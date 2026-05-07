# ═══════════════════════════════════════════════════════════
# CONSUMER360: WEEK 1 - DATA CLEANING
# Purpose: Clean raw data and save to a CSV file
# ═══════════════════════════════════════════════════════════

import pandas as pd

print("Starting data cleaning process...")

# 1. Load the raw data
print("Loading raw data from Excel file...")
df = pd.read_excel('data/raw/online_retail_II.xlsx')
print(f"Original rows: {len(df)}")

# 2. Fix the column names (make them lowercase and remove spaces)
df.columns = df.columns.str.lower().str.replace(' ', '_')
if 'invoice_date' in df.columns:
    df.rename(columns={'invoice_date': 'invoicedate'}, inplace=True)

# 3. Remove cancelled orders (invoices starting with 'C')
df = df[~df['invoice'].astype(str).str.startswith('C')]

# 4. Drop rows that don't have a customer ID
df = df.dropna(subset=['customer_id'])

# 5. Remove bad data (negative/zero quantities and prices)
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df = df[(df['quantity'] > 0) & (df['price'] > 0)]

# 6. Fix data types
df['customer_id'] = df['customer_id'].astype(int)
df['invoicedate'] = pd.to_datetime(df['invoicedate'])

# 7. Add useful calculated columns
df['total_amount'] = df['quantity'] * df['price']
df['date_only'] = df['invoicedate'].dt.date

print(f"Data cleaned! Remaining rows: {len(df)}")

# 8. Save the cleaned data to a new CSV file
print("Saving cleaned data to CSV...")
df.to_csv('data/processed/cleaned_retail.csv', index=False)

# 9. Upload the cleaned data to SQL Server
print("Uploading cleaned data to SQL Server...")
try:
    import data_loader
    data_loader.load_to_sql_server(df)
    print("Data uploaded to SQL Server successfully!")
except Exception as e:
    print(f"Error uploading to SQL Server: {e}")

print("\nAll done!")
