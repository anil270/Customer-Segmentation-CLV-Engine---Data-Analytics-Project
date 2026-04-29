# ═══════════════════════════════════════════════════════════
# CONSUMER360: WEEK 2 - RFM ANALYSIS (SQL SERVER)
# Purpose: Calculate RFM scores and segment customers
# ═══════════════════════════════════════════════════════════

import pandas as pd
import pyodbc
from datetime import datetime
import numpy as np

print("="*70)
print("CONSUMER360: WEEK 2 - RFM ANALYSIS")
print("="*70)

# ══════════════════════════════════════════════════════════════
# STEP 1: CONNECT TO SQL SERVER
# ══════════════════════════════════════════════════════════════
import warnings

# Suppress pandas SQL warning for pyodbc
warnings.filterwarnings('ignore', category=UserWarning, message='.*pandas only supports SQLAlchemy connectable.*')   

print("\n[STEP 1] Connecting to SQL Server...")

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
    print("✓ Connection successful!")
    print(f"✓ Connected to SQL Server: {SERVER}")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fact_sales")
    for row in cursor.fetchall():
        print(row)

except Exception as e:
    print(f"✗ Error: {e}")



# ══════════════════════════════════════════════════════════════
# STEP 2: LOAD FACT_SALES DATA
# ══════════════════════════════════════════════════════════════

print("\n[STEP 2] Loading fact_sales data...")

query = """
SELECT 
    f.customer_id,
    f.invoice_id,
    f.invoice_date,
    f.total_amount,
    c.country
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
"""

try:
    df = pd.read_sql(query, conn)
    print(f"✓ Loaded {len(df):,} transactions")
    print(f"  - Unique customers: {df['customer_id'].nunique():,}")
    print(f"  - Date range: {df['invoice_date'].min()} to {df['invoice_date'].max()}")
except Exception as e:
    print(f"✗ Error loading data: {e}")
    exit()

# ══════════════════════════════════════════════════════════════
# STEP 3: CALCULATE RFM METRICS
# ══════════════════════════════════════════════════════════════

print("\n[STEP 3] Calculating RFM metrics...")

# Reference date (last date in dataset)
reference_date = pd.to_datetime('2011-12-31')

# Group by customer
rfm = df.groupby('customer_id').agg({
    'invoice_date': 'max',  # Last purchase date
    'invoice_id': 'nunique',  # Number of purchases
    'total_amount': 'sum',  # Total spent
    'country': 'first'  # Country
}).reset_index()

rfm.columns = ['customer_id', 'last_purchase_date', 'frequency', 'monetary', 'country']

# Calculate recency (days since last purchase)
rfm['recency'] = (reference_date - pd.to_datetime(rfm['last_purchase_date'])).dt.days

print(f"✓ RFM metrics calculated")
print(f"  - Recency range: {rfm['recency'].min()} to {rfm['recency'].max()} days")
print(f"  - Frequency range: {rfm['frequency'].min()} to {rfm['frequency'].max()} purchases")
print(f"  - Monetary range: £{rfm['monetary'].min():.2f} to £{rfm['monetary'].max():.2f}")

# ══════════════════════════════════════════════════════════════
# STEP 4: CALCULATE RFM SCORES (1-5 SCALE)
# ══════════════════════════════════════════════════════════════

print("\n[STEP 4] Calculating RFM scores (1-5 scale)...")

# Recency: Lower days = Higher score (5 = most recent)
# We use rank to handle ties properly
rfm['r_score'] = pd.qcut(rfm['recency'].rank(method='first'), q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')

# Frequency: Higher frequency = Higher score (5 = most frequent)
rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

# Monetary: Higher spending = Higher score (5 = highest spender)
rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

# Convert to integer
rfm['r_score'] = rfm['r_score'].astype(int)
rfm['f_score'] = rfm['f_score'].astype(int)
rfm['m_score'] = rfm['m_score'].astype(int)

print(f"✓ RFM scores calculated")
print(f"  - R_score range: {rfm['r_score'].min()} to {rfm['r_score'].max()}")
print(f"  - F_score range: {rfm['f_score'].min()} to {rfm['f_score'].max()}")
print(f"  - M_score range: {rfm['m_score'].min()} to {rfm['m_score'].max()}")

# ══════════════════════════════════════════════════════════════
# STEP 5: CREATE RFM SEGMENTS
# ══════════════════════════════════════════════════════════════

print("\n[STEP 5] Creating customer segments...")

def assign_segment(r, f, m):
    """
    Assign customer segment based on RFM scores
    """
    if r == 5 and f == 5 and m == 5:
        return 'Champions'
    elif r == 5 and f >= 4 and m >= 4:
        return 'Loyal Customers'
    elif r >= 4 and f == 5 and m == 5:
        return 'Potential Loyalist'
    elif r == 1 and f == 1 and m == 1:
        return 'Lost'
    elif r == 1 and f >= 4 and m >= 4:
        return 'Can\'t Lose Them'
    elif r >= 4 and f == 1 and m == 1:
        return 'Recent Users'
    elif r >= 4 and f >= 3 and m >= 3:
        return 'Promising'
    elif r == 2 and f >= 3 and m >= 3:
        return 'Needs Attention'
    elif r >= 3 and f == 2 and m == 2:
        return 'About To Sleep'
    elif r >= 3 and f >= 2 and m >= 2:
        return 'Hibernating'
    else:
        return 'Price Sensitive'

# Apply segment function
rfm['segment'] = rfm.apply(lambda x: assign_segment(x['r_score'], x['f_score'], x['m_score']), axis=1)

print(f"✓ Customer segments created")
print(f"\nSegment Distribution:")
segment_counts = rfm['segment'].value_counts()
for segment, count in segment_counts.items():
    pct = (count / len(rfm)) * 100
    print(f"  - {segment}: {count:,} customers ({pct:.1f}%)")

# ══════════════════════════════════════════════════════════════
# STEP 6: ANALYZE SEGMENTS
# ══════════════════════════════════════════════════════════════

print("\n[STEP 6] Analyzing segments...")

segment_analysis = rfm.groupby('segment').agg({
    'customer_id': 'count',
    'recency': 'mean',
    'frequency': 'mean',
    'monetary': ['mean', 'sum']
}).round(2)

segment_analysis.columns = ['Customer Count', 'Avg Recency (days)', 'Avg Frequency', 'Avg Monetary (£)', 'Total Revenue (£)']
segment_analysis = segment_analysis.sort_values('Total Revenue (£)', ascending=False)

print("\nSegment Analysis:")
print(segment_analysis.to_string())

# ══════════════════════════════════════════════════════════════
# STEP 7: SAVE RFM RESULTS
# ══════════════════════════════════════════════════════════════

print("\n[STEP 7] Saving RFM results...")

# Save full RFM data
rfm_output = rfm[[
    'customer_id', 'country', 'last_purchase_date', 'recency', 
    'frequency', 'monetary', 'r_score', 'f_score', 'm_score', 'segment'
]].sort_values('monetary', ascending=False)

output_path = 'data/processed/rfm_segmentation.csv'
rfm_output.to_csv(output_path, index=False)
print(f"✓ Saved to: {output_path}")

# ══════════════════════════════════════════════════════════════
# STEP 8: LOAD RFM INTO SQL SERVER
# ══════════════════════════════════════════════════════════════

print("\n[STEP 8] Loading RFM results into SQL Server...")

# Create RFM table if not exists
create_table_sql = """
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'rfm_segmentation')
CREATE TABLE rfm_segmentation (
    customer_id INT PRIMARY KEY,
    country VARCHAR(100),
    last_purchase_date DATE,
    recency INT,
    frequency INT,
    monetary DECIMAL(10,2),
    r_score INT,
    f_score INT,
    m_score INT,
    segment VARCHAR(50)
);
"""

try:
    cursor.execute(create_table_sql)
    conn.commit()
    print("✓ RFM table created/verified")
except Exception as e:
    print(f"✗ Error creating table: {e}")

# Clear existing data
cursor.execute("DELETE FROM rfm_segmentation")

# Insert new data
insert_sql = """
INSERT INTO rfm_segmentation 
(customer_id, country, last_purchase_date, recency, frequency, monetary, r_score, f_score, m_score, segment)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

for idx, row in rfm_output.iterrows():
    cursor.execute(insert_sql,
        row['customer_id'],
        row['country'],
        row['last_purchase_date'],
        row['recency'],
        row['frequency'],
        row['monetary'],
        row['r_score'],
        row['f_score'],
        row['m_score'],
        row['segment']
    )

conn.commit()
print(f"✓ Loaded {len(rfm_output):,} customer records into SQL Server")

# ══════════════════════════════════════════════════════════════
# STEP 9: KEY INSIGHTS
# ══════════════════════════════════════════════════════════════

print("\n[STEP 9] Key Insights:")

# Champions
champions = rfm[rfm['segment'] == 'Champions']
print(f"\n  Champions ({len(champions)} customers):")
print(f"    - Avg Revenue: £{champions['monetary'].mean():.2f}")
print(f"    - Total Revenue: £{champions['monetary'].sum():.2f}")
print(f"    - Avg Purchases: {champions['frequency'].mean():.1f}")
print(f"    - Action: VIP treatment, loyalty rewards")

# Can't Lose Them
cant_lose = rfm[rfm['segment'] == 'Can\'t Lose Them']
if len(cant_lose) > 0:
    print(f"\n  Can't Lose Them ({len(cant_lose)} customers):")
    print(f"    - Avg Revenue: £{cant_lose['monetary'].mean():.2f}")
    print(f"    - Total Revenue: £{cant_lose['monetary'].sum():.2f}")
    print(f"    - Avg Days Since Purchase: {cant_lose['recency'].mean():.0f}")
    print(f"    - Action: Win-back campaigns, special offers")

# Recent Users
recent = rfm[rfm['segment'] == 'Recent Users']
if len(recent) > 0:
    print(f"\n  Recent Users ({len(recent)} customers):")
    print(f"    - Avg Revenue: £{recent['monetary'].mean():.2f}")
    print(f"    - Total Revenue: £{recent['monetary'].sum():.2f}")
    print(f"    - Action: Convert to frequent buyers")

# Lost
lost = rfm[rfm['segment'] == 'Lost']
if len(lost) > 0:
    print(f"\n  Lost ({len(lost)} customers):")
    print(f"    - Avg Revenue: £{lost['monetary'].mean():.2f}")
    print(f"    - Total Revenue: £{lost['monetary'].sum():.2f}")
    print(f"    - Avg Days Since Purchase: {lost['recency'].mean():.0f}")
    print(f"    - Action: Re-engagement campaigns")

# ══════════════════════════════════════════════════════════════
# STEP 10: TOP CUSTOMERS BY SEGMENT
# ══════════════════════════════════════════════════════════════

print("\n[STEP 10] Top 3 Customers by Segment:")

for segment in rfm['segment'].unique():
    segment_data = rfm[rfm['segment'] == segment].sort_values('monetary', ascending=False).head(3)
    print(f"\n  {segment}:")
    for idx, (_, row) in enumerate(segment_data.iterrows(), 1):
        print(f"    {idx}. Customer {row['customer_id']}: £{row['monetary']:.2f} ({row['frequency']} purchases)")

conn.close()

# ══════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════