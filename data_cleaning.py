# ═══════════════════════════════════════════════════════════
# CONSUMER360: WEEK 1 - DATA CLEANING & LOADING (SQL SERVER)
# ═══════════════════════════════════════════════════════════

import pandas as pd
import pyodbc
from datetime import datetime
import sys

# Force UTF-8 encoding for standard output to support symbols in Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("="*70)
print("CONSUMER360: WEEK 1 - DATA CLEANING & LOADING (SQL SERVER)")
print("="*70)

# ══════════════════════════════════════════════════════════════
# STEP 1: LOAD RAW DATA
# ══════════════════════════════════════════════════════════════

print("\n[STEP 1] Loading raw data from Excel...")

try:
    df = pd.read_excel("data/raw/online_retail_II.xlsx")
    print(f"✓ Successfully loaded data")
    print(f"  - Rows: {len(df):,}")
    print(f"  - Columns: {len(df.columns)}")
    print(f"  - Column names: {list(df.columns)}")
except Exception as e:
    print(f"✗ Error loading file: {e}")
    print("  Make sure online_retail_II.xlsx is in data/raw/ folder")
    exit()

# ══════════════════════════════════════════════════════════════
# STEP 2: STANDARDIZE COLUMN NAMES
# ══════════════════════════════════════════════════════════════

print("\n[STEP 2] Standardizing column names...")

df.columns = df.columns.str.lower().str.replace(' ', '_')

print(f"✓ Column names standardized")

# ══════════════════════════════════════════════════════════════
# STEP 3: REMOVE CANCELLED ORDERS
# ══════════════════════════════════════════════════════════════

print("\n[STEP 3] Removing cancelled orders...")

initial_count = len(df)
df = df[~df['invoice'].astype(str).str.startswith('C')]
removed_count = initial_count - len(df)

print(f"✓ Removed {removed_count:,} cancelled orders")
print(f"  - Before: {initial_count:,} rows")
print(f"  - After: {len(df):,} rows")

# ══════════════════════════════════════════════════════════════
# STEP 4: REMOVE ROWS WITH MISSING CUSTOMER ID
# ══════════════════════════════════════════════════════════════

print("\n[STEP 4] Removing rows with missing Customer ID...")

initial_count = len(df)
df = df.dropna(subset=['customer_id'])
removed_count = initial_count - len(df)

print(f"✓ Removed {removed_count:,} rows with missing Customer ID")
print(f"  - Before: {initial_count:,} rows")
print(f"  - After: {len(df):,} rows")

# ══════════════════════════════════════════════════════════════
# STEP 5: REMOVE INVALID QUANTITIES
# ══════════════════════════════════════════════════════════════

print("\n[STEP 5] Removing rows with invalid quantities...")

initial_count = len(df)
df = df[df['quantity'] > 0]
removed_count = initial_count - len(df)

print(f"✓ Removed {removed_count:,} rows with invalid quantity")
print(f"  - Before: {initial_count:,} rows")
print(f"  - After: {len(df):,} rows")

# ══════════════════════════════════════════════════════════════
# STEP 6: REMOVE INVALID PRICES
# ══════════════════════════════════════════════════════════════

print("\n[STEP 6] Removing rows with invalid prices...")

initial_count = len(df)
df = df[df['price'] > 0]
removed_count = initial_count - len(df)

print(f"✓ Removed {removed_count:,} rows with invalid price")
print(f"  - Before: {initial_count:,} rows")
print(f"  - After: {len(df):,} rows")

# ══════════════════════════════════════════════════════════════
# STEP 7: CONVERT DATA TYPES
# ══════════════════════════════════════════════════════════════

print("\n[STEP 7] Converting data types...")

df['customer_id'] = df['customer_id'].astype(int)
df['invoicedate'] = pd.to_datetime(df['invoicedate'])
df['quantity'] = df['quantity'].astype(int)
df['price'] = df['price'].astype(float)

print(f"✓ Data types converted successfully")

# ══════════════════════════════════════════════════════════════
# STEP 8: CREATE CALCULATED COLUMNS
# ══════════════════════════════════════════════════════════════

print("\n[STEP 8] Creating calculated columns...")

df['total_amount'] = df['quantity'] * df['price']
df['year'] = df['invoicedate'].dt.year
df['month'] = df['invoicedate'].dt.month
df['date_only'] = df['invoicedate'].dt.date

print(f"✓ Calculated columns created")

# ══════════════════════════════════════════════════════════════
# STEP 9: SAVE CLEANED DATA TO CSV
# ══════════════════════════════════════════════════════════════

print("\n[STEP 9] Saving cleaned data to CSV...")

output_path = "data/processed/cleaned_retail.csv"
df.to_csv(output_path, index=False)

print(f"✓ Cleaned data saved to: {output_path}")

# ══════════════════════════════════════════════════════════════
# STEP 10: CONNECT TO SQL SERVER
# ══════════════════════════════════════════════════════════════

print("\n[STEP 10] Connecting to SQL Server...")

# Update these with your SQL Server details
import pyodbc
SERVER = r'DESKTOP-94L3J1Q\SQLEXPRESS'
DATABASE = 'Consumer360'

try:
    conn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};'
        f'Server={SERVER};'
        f'Database={DATABASE};'
        'Trusted_Connection=yes;'
        'Encrypt=no;'
    )
    print("✓ Connected successfully!")
    
    cursor = conn.cursor()
    cursor.execute('SELECT TOP 5 * FROM dim_customer')
    for row in cursor.fetchall():
        print(row)
except Exception as e:
    print(f"✗ Error: {e}")

# ══════════════════════════════════════════════════════════════
# STEP 11: LOAD DIM_CUSTOMER
# ══════════════════════════════════════════════════════════════
print("\n[STEP 11] Loading DIM_CUSTOMER...")

dim_customer = df[['customer_id', 'country']].drop_duplicates(subset=['customer_id'])
first_purchase = df.groupby('customer_id')['invoicedate'].min().reset_index()
first_purchase.columns = ['customer_id', 'first_purchase_date']
dim_customer = dim_customer.merge(first_purchase, on='customer_id')

# Wrap the entire DB operation in a connection context
with conn:  # This will automatically commit on success or rollback on error
    cursor = conn.cursor()
    # Delete from fact_sales first to avoid foreign key reference errors
    cursor.execute("DELETE FROM fact_sales")
    cursor.execute("DELETE FROM dim_customer")

    # Use executemany for faster inserts without fast_executemany hangs
    customer_data = list(dim_customer[['customer_id', 'country', 'first_purchase_date']].itertuples(index=False, name=None))
    cursor.executemany("""
        INSERT INTO dim_customer (customer_id, country, first_purchase_date)
        VALUES (?, ?, ?)
    """, customer_data)

print(f"✓ Loaded {len(dim_customer):,} unique customers")

# ══════════════════════════════════════════════════════════════
# STEP 12: LOAD DIM_PRODUCT
# ══════════════════════════════════════════════════════════════

print("\n[STEP 12] Loading DIM_PRODUCT...")

dim_product = df[['stockcode', 'description']].drop_duplicates(subset=['stockcode'])
dim_product.columns = ['product_id', 'description']
dim_product['category'] = 'General'

# Clear existing data
cursor.execute("DELETE FROM dim_product")

# Insert new data
product_data = list(dim_product[['product_id', 'description', 'category']].itertuples(index=False, name=None))
cursor.executemany("""
    INSERT INTO dim_product (product_id, description, category)
    VALUES (?, ?, ?)
""", product_data)

conn.commit()
print(f"✓ Loaded {len(dim_product):,} unique products")

# ══════════════════════════════════════════════════════════════
# STEP 13: LOAD DIM_DATE
# ══════════════════════════════════════════════════════════════

print("\n[STEP 13] Loading DIM_DATE...")

date_min = df['invoicedate'].min()
date_max = df['invoicedate'].max()
date_range = pd.date_range(start=date_min, end=date_max, freq='D')

dim_date = pd.DataFrame({
    'date_id': date_range.date,
    'day': date_range.day,
    'month': date_range.month,
    'quarter': date_range.quarter,
    'year': date_range.year,
    'week_of_year': date_range.isocalendar().week.astype(int),
    'day_of_week': date_range.day_name(),
    'is_weekend': (date_range.dayofweek >= 5).astype(int)
})

# Clear existing data
cursor.execute("DELETE FROM dim_date")

# Insert new data
date_data = list(dim_date[['date_id', 'day', 'month', 'quarter', 'year', 'week_of_year', 'day_of_week', 'is_weekend']].itertuples(index=False, name=None))
cursor.executemany("""
    INSERT INTO dim_date (date_id, day, month, quarter, year, week_of_year, day_of_week, is_weekend)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", date_data)

conn.commit()
print(f"✓ Loaded {len(dim_date):,} date records")

# ══════════════════════════════════════════════════════════════
# STEP 14: LOAD FACT_SALES
# ══════════════════════════════════════════════════════════════

print("\n[STEP 14] Loading FACT_SALES...")

fact_sales = df[[
    'invoice', 'customer_id', 'stockcode', 
    'date_only', 'quantity', 'price', 'total_amount'
]].copy()

fact_sales.columns = [
    'invoice_id', 'customer_id', 'product_id', 
    'invoice_date', 'quantity', 'unit_price', 'total_amount'
]

# Clear existing data has already been handled in Step 11

# Insert new data
# Chunking fact_sales inserts to avoid memory issues and print progress
total_rows = len(fact_sales)
chunk_size = 50000
for i in range(0, total_rows, chunk_size):
    chunk = fact_sales.iloc[i:i + chunk_size]
    sales_data = list(chunk[['invoice_id', 'customer_id', 'product_id', 'invoice_date', 'quantity', 'unit_price', 'total_amount']].itertuples(index=False, name=None))
    cursor.executemany("""
        INSERT INTO fact_sales (invoice_id, customer_id, product_id, invoice_date, quantity, unit_price, total_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sales_data)
    print(f"  ... inserted {min(i + chunk_size, total_rows):,} / {total_rows:,} rows")

conn.commit()
print(f"✓ Loaded {len(fact_sales):,} transaction records")

# ══════════════════════════════════════════════════════════════
# STEP 15: DATA QUALITY VERIFICATION
# ══════════════════════════════════════════════════════════════

print("\n[STEP 15] Verifying data quality...")

# Check table counts
tables = ['dim_customer', 'dim_product', 'dim_date', 'fact_sales']
print("\n  Table Record Counts:")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) as cnt FROM {table}")
    count = cursor.fetchone()
    print(f"    ✓ {table.upper()}: {count[0]:,} records")

# Check for NULL values
print("\n  NULL Value Checks:")
cursor.execute("""
    SELECT 
        COUNT(*) as total_records,
        SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_customer_id,
        SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) as null_product_id,
        SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END) as null_total_amount
    FROM fact_sales
""")

result = cursor.fetchone()
print(f"    ✓ Total Sales Records: {result[0]:,}")
print(f"    ✓ Null CustomerID: {result[1]}")
print(f"    ✓ Null ProductID: {result[2]}")
print(f"    ✓ Null TotalAmount: {result[3]}")

# Check data ranges
print("\n  Data Range Checks:")
cursor.execute("""
    SELECT 
        MIN(invoice_date) as min_date,
        MAX(invoice_date) as max_date,
        MIN(total_amount) as min_amount,
        MAX(total_amount) as max_amount
    FROM fact_sales
""")

result = cursor.fetchone()
print(f"    ✓ Date Range: {result[0]} to {result[1]}")
print(f"    ✓ Amount Range: £{result[2]:.2f} to £{result[3]:.2f}")

conn.close()

# ══════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════