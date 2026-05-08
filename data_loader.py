# ═══════════════════════════════════════════════════════════
# CONSUMER360: DATA LOADER
# Purpose: Upload cleaned data into SQL Server Star Schema
# ═══════════════════════════════════════════════════════════

import pandas as pd
import urllib.parse
from sqlalchemy import create_engine, text

def load_to_sql_server(df):
    print("\n--- Starting Database Upload Process ---")
    
    # 1. Connect & Clear Old Data
    SERVER, DATABASE = r"DESKTOP-94L3J1Q\SQLEXPRESS", "Consumer360"
    params = urllib.parse.quote_plus(f"Driver={{ODBC Driver 17 for SQL Server}};Server={SERVER};Database={DATABASE};Trusted_Connection=yes;Encrypt=no;")
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)
    
    print("Clearing old data from tables...")
    with engine.begin() as conn:
        tables_to_clear = ["fact_sales", "rfm_segmentation", "dim_customer", "dim_product", "dim_date"]
        for table in tables_to_clear:
            try: conn.execute(text(f"DELETE FROM {table}"))
            except: pass # Ignore if table doesn't exist yet

    # 2. Upload DIM_CUSTOMER
    print("Uploading dim_customer...")
    # Smart aggregation to get country and first purchase date in one line
    dim_cust = df.groupby('customer_id').agg(country=('country', 'first'), first_purchase_date=('invoicedate', 'min')).reset_index()
    dim_cust['first_purchase_date'] = pd.to_datetime(dim_cust['first_purchase_date']).dt.date
    dim_cust.to_sql('dim_customer', engine, if_exists='append', index=False)

    # 3. Upload DIM_PRODUCT
    print("Uploading dim_product...")
    dim_prod = df[['stockcode', 'description']].drop_duplicates('stockcode').rename(columns={'stockcode': 'product_id'})
    dim_prod['category'] = 'General'
    dim_prod['description'] = dim_prod['description'].astype(str).str.slice(0, 4000)
    dim_prod.to_sql('dim_product', engine, if_exists='append', index=False)

    # 4. Upload DIM_DATE
    print("Uploading dim_date...")
    dates = pd.date_range(start=df['invoicedate'].min(), end=df['invoicedate'].max(), freq='D')
    dim_date = pd.DataFrame({
        'date_id': dates.date, 'day': dates.day, 'month': dates.month, 'quarter': dates.quarter, 
        'year': dates.year, 'week_of_year': dates.isocalendar().week.astype(int), 
        'day_of_week': dates.day_name(), 'is_weekend': (dates.dayofweek >= 5).astype(int)
    })
    dim_date.to_sql('dim_date', engine, if_exists='append', index=False)

    # 5. Upload FACT_SALES
    print("Uploading fact_sales (This may take a moment)...")
    fact = df[['invoice', 'customer_id', 'stockcode', 'date_only', 'quantity', 'price', 'total_amount']].rename(
        columns={'invoice': 'invoice_id', 'stockcode': 'product_id', 'date_only': 'invoice_date', 'price': 'unit_price'}
    )
    fact.to_sql('fact_sales', engine, if_exists='append', index=False, chunksize=20000)

    print("--- Database Upload Complete! ---")