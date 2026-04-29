# ═══════════════════════════════════════════════════════════
# CONSUMER360: MASTER AUTOMATION SCRIPT (ETL + RFM + MBA)
# Purpose: Master script to automate entire pipeline
# Runs: Every Sunday 11 PM automatically
# ═══════════════════════════════════════════════════════════

import pandas as pd
import pyodbc
import os
import sys
from datetime import datetime
import logging
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

# ══════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════
EXCEL_FILE = "data/raw/online_retail_II.xlsx"
SERVER = r'DESKTOP-94L3J1Q\SQLEXPRESS'
DATABASE = 'Consumer360'

# ══════════════════════════════════════════════════════════════
# SETUP LOGGING
# ══════════════════════════════════════════════════════════════
os.makedirs("logs", exist_ok=True)
log_file = f"logs/master_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("="*70)
    logger.info("CONSUMER360: AUTOMATION PIPELINE STARTED")
    logger.info("="*70)

    # ══════════════════════════════════════════════════════════════
    # STEP 1: LOAD RAW DATA
    # ══════════════════════════════════════════════════════════════
    logger.info("\n[STEP 1] Loading raw data from Excel...")
    try:
        # Load specific sheet to ensure accuracy
        df = pd.read_excel(EXCEL_FILE)
        logger.info(f"Successfully loaded {len(df):,} rows from {EXCEL_FILE}")
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return

    # ══════════════════════════════════════════════════════════════
    # STEP 2: DATA CLEANING
    # ══════════════════════════════════════════════════════════════
    logger.info("\n[STEP 2] Cleaning and preparing data...")
    try:
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Remove cancellations and invalid records
        initial_count = len(df)
        df = df[~df['invoice'].astype(str).str.startswith('C')]
        df = df.dropna(subset=['customer_id', 'invoice', 'stockcode'])
        df = df[df['quantity'] > 0]
        df = df[df['price'] > 0]
        
        # Data types
        df['customer_id'] = df['customer_id'].astype(int)
        df['invoicedate'] = pd.to_datetime(df['invoicedate'])
        df['total_amount'] = df['quantity'] * df['price']
        df['date_only'] = df['invoicedate'].dt.date
        
        logger.info(f"Data cleaned. Rows remaining: {len(df):,} (Removed {initial_count - len(df):,} invalid rows)")
    except Exception as e:
        logger.error(f"Error during cleaning: {e}")
        return

    # ══════════════════════════════════════════════════════════════
    # STEP 3: DATABASE CONNECTION
    # ══════════════════════════════════════════════════════════════
    logger.info("\n[STEP 3] Connecting to SQL Server...")
    try:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str, autocommit=False)
        cursor = conn.cursor()
        logger.info(f"Connected to {DATABASE} on {SERVER}")
    except Exception as e:
        logger.error(f"Database Connection Failed: {e}")
        return

    # ══════════════════════════════════════════════════════════════
    # STEP 4: LOAD DIMENSIONS (OPTIMIZED)
    # ══════════════════════════════════════════════════════════════
    logger.info("\n[STEP 4] Loading Dimensions to SQL Server...")
    try:
        # Clear existing data in correct order
        cursor.execute("DELETE FROM fact_sales")
        cursor.execute("DELETE FROM rfm_segmentation")
        cursor.execute("DELETE FROM dim_customer")
        cursor.execute("DELETE FROM dim_product")
        cursor.execute("DELETE FROM dim_date")
        conn.commit()

        # DIM_CUSTOMER
        logger.info("  - Loading DIM_CUSTOMER...")
        dim_cust = df[['customer_id', 'country']].drop_duplicates(subset=['customer_id'])
        first_date = df.groupby('customer_id')['invoicedate'].min().reset_index()
        dim_cust = dim_cust.merge(first_date, on='customer_id')
        dim_cust = dim_cust.drop_duplicates(subset=['customer_id']) # Final safety check
        
        cursor.fast_executemany = False # Required for customer truncation fix
        cust_params = dim_cust[['customer_id', 'country', 'invoicedate']].values.tolist()
        cursor.executemany("INSERT INTO dim_customer (customer_id, country, first_purchase_date) VALUES (?, ?, ?)", cust_params)
        
        # DIM_PRODUCT
        logger.info("  - Loading DIM_PRODUCT...")
        dim_prod = df[['stockcode', 'description']].drop_duplicates(subset=['stockcode'])
        # Fix for fast_executemany buffer: Pad strings
        dim_prod['description'] = dim_prod['description'].astype(str).str.ljust(100)
        dim_prod['stockcode'] = dim_prod['stockcode'].astype(str).str.ljust(20)
        
        cursor.fast_executemany = True
        prod_params = [(str(row[0]), str(row[1]), 'General') for row in dim_prod.itertuples(index=False)]
        cursor.executemany("INSERT INTO dim_product (product_id, description, category) VALUES (?, ?, ?)", prod_params)

        # DIM_DATE
        logger.info("  - Loading DIM_DATE...")
        d_min, d_max = df['invoicedate'].min(), df['invoicedate'].max()
        d_range = pd.date_range(start=d_min, end=d_max, freq='D')
        date_data = [(d.date(), d.day, d.month, (d.month-1)//3 + 1, d.year, d.isocalendar().week, d.day_name(), int(d.dayofweek >= 5)) for d in d_range]
        cursor.executemany("INSERT INTO dim_date (date_id, day, month, quarter, year, week_of_year, day_of_week, is_weekend) VALUES (?,?,?,?,?,?,?,?)", date_data)
        
        conn.commit()
        logger.info("Dimensions loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading dimensions: {e}")
        conn.rollback()
        return

    # ══════════════════════════════════════════════════════════════
    # STEP 5: LOAD FACT_SALES (BULK OPTIMIZED)
    # ══════════════════════════════════════════════════════════════
    logger.info("\n[STEP 5] Loading FACT_SALES (Bulk Mode)...")
    try:
        fact_sales = df[['invoice', 'customer_id', 'stockcode', 'date_only', 'quantity', 'price', 'total_amount']].copy()
        sales_params = fact_sales.values.tolist()
        
        chunk_size = 10000
        for i in range(0, len(sales_params), chunk_size):
            chunk = sales_params[i:i + chunk_size]
            cursor.executemany("INSERT INTO fact_sales (invoice_id, customer_id, product_id, invoice_date, quantity, unit_price, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)", chunk)
            if i % 50000 == 0: logger.info(f"  ... Loaded {min(i + chunk_size, len(sales_params)):,} rows")
        
        conn.commit()
        logger.info(f"Successfully loaded {len(sales_params):,} transactions.")
    except Exception as e:
        logger.error(f"Error loading fact_sales: {e}")
        conn.rollback()
        return

    # ══════════════════════════════════════════════════════════════
    # STEP 6: RFM ANALYSIS
    # ══════════════════════════════════════════════════════════════
    logger.info("\n[STEP 6] Calculating RFM Analysis...")
    try:
        ref_date = df['invoicedate'].max() + pd.Timedelta(days=1)
        rfm = df.groupby('customer_id').agg({
            'invoicedate': lambda x: (ref_date - x.max()).days,
            'invoice': 'nunique',
            'total_amount': 'sum',
            'country': 'first'
        }).reset_index()
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary', 'country']
        
        # Scoring (1-5)
        rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
        
        def get_segment(row):
            r, f = int(row['r_score']), int(row['f_score'])
            if r >= 4 and f >= 4: return 'Champions'
            if r >= 3 and f >= 3: return 'Loyal Customers'
            if r >= 4 and f <= 2: return 'Recent Users'
            if r <= 2 and f >= 4: return 'At Risk'
            if r <= 2 and f <= 2: return 'Lost'
            return 'Hibernating'

        rfm['segment'] = rfm.apply(get_segment, axis=1)
        
        # Load RFM to SQL
        rfm_params = [(r.customer_id, r.country, r.recency, r.frequency, r.monetary, int(r.r_score), int(r.f_score), int(r.m_score), r.segment) for r in rfm.itertuples(index=False)]
        cursor.executemany("INSERT INTO rfm_segmentation (customer_id, country, recency, frequency, monetary, r_score, f_score, m_score, segment) VALUES (?,?,?,?,?,?,?,?,?)", rfm_params)
        conn.commit()
        
        logger.info(f"RFM complete: {len(rfm):,} customers segmented.")
    except Exception as e:
        logger.error(f"RFM Analysis failed: {e}")

    # ══════════════════════════════════════════════════════════════
    # STEP 7: MARKET BASKET ANALYSIS (MBA)
    # ══════════════════════════════════════════════════════════════
    logger.info("\n[STEP 7] Market Basket Analysis...")
    try:
        basket = df.groupby(['invoice', 'stockcode'])['quantity'].count().unstack().reset_index().fillna(0).set_index('invoice')
        # Use .map() instead of deprecated .applymap() and convert to bool
        basket_encoded = basket.map(lambda x: 1 if x > 0 else 0).astype(bool)
        
        freq_items = apriori(basket_encoded, min_support=0.03, use_colnames=True)
        rules = association_rules(freq_items, metric="lift", min_threshold=1)
        rules.to_csv("data/processed/market_basket_rules.csv", index=False)
        logger.info(f"MBA complete. Found {len(rules)} rules. Saved to CSV.")
    except Exception as e:
        logger.error(f"MBA failed: {e}")

    # ══════════════════════════════════════════════════════════════
    # STEP 8: POWER BI REFRESH
    # ══════════════════════════════════════════════════════════════
    logger.info("\n[STEP 8] Power BI refresh...")
    logger.info("Power BI will auto-refresh on next open")

    # ══════════════════════════════════════════════════════════════
    # FINAL
    # ══════════════════════════════════════════════════════════════
    conn.close()
    logger.info("\n" + "="*70)
    logger.info("AUTOMATION PIPELINE COMPLETED SUCCESSFULLY")
    logger.info(f"Log: {log_file}")
    logger.info("="*70 + "\n")

if __name__ == "__main__":
    run_pipeline()