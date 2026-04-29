# ═══════════════════════════════════════════════════════════
# CONSUMER360: WEEK 2 - MARKET BASKET ANALYSIS
# Purpose: Find products frequently bought together
# ═══════════════════════════════════════════════════════════

import pandas as pd
import pyodbc
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder
import numpy as np
import warnings

# Suppress pandas SQL warning for pyodbc
warnings.filterwarnings('ignore', category=UserWarning, message='.*pandas only supports SQLAlchemy connectable.*')

print("="*70)
print("CONSUMER360: WEEK 2 - MARKET BASKET ANALYSIS")
print("="*70)

# ══════════════════════════════════════════════════════════════
# STEP 1: CONNECT TO SQL SERVER
# ══════════════════════════════════════════════════════════════

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
    print(f"✓ Connected to SQL Server")

except Exception as e:
    print(f"✗ Error: {e}")
    exit()

# ══════════════════════════════════════════════════════════════
# STEP 2: LOAD TRANSACTION DATA
# ══════════════════════════════════════════════════════════════

print("\n[STEP 2] Loading transaction data...")

query = """
SELECT 
    f.invoice_id,
    f.product_id,
    p.description
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
ORDER BY f.invoice_id, f.product_id
"""

df = pd.read_sql(query, conn)
print(f"✓ Loaded {len(df):,} transaction items")
print(f"  - Unique invoices: {df['invoice_id'].nunique():,}")
print(f"  - Unique products: {df['product_id'].nunique():,}")

# ══════════════════════════════════════════════════════════════
# STEP 3: CREATE TRANSACTION-PRODUCT MATRIX
# ══════════════════════════════════════════════════════════════

print("\n[STEP 3] Creating transaction-product matrix...")

# Group products by invoice
transactions = df.groupby('invoice_id')['product_id'].apply(list).values

print(f"✓ Created {len(transactions):,} transactions")
print(f"  - Avg items per transaction: {np.mean([len(t) for t in transactions]):.2f}")

# ══════════════════════════════════════════════════════════════
# STEP 4: ONE-HOT ENCODE TRANSACTIONS
# ══════════════════════════════════════════════════════════════

print("\n[STEP 4] One-hot encoding transactions...")

te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

print(f"✓ Encoded matrix shape: {df_encoded.shape}")
print(f"  - Transactions: {df_encoded.shape[0]:,}")
print(f"  - Products: {df_encoded.shape[1]:,}")

# ══════════════════════════════════════════════════════════════
# STEP 5: APPLY APRIORI ALGORITHM
# ══════════════════════════════════════════════════════════════

print("\n[STEP 5] Applying FP-Growth algorithm (memory efficient)...")

# Find frequent itemsets (min 1% support)
frequent_itemsets = fpgrowth(df_encoded, min_support=0.01, use_colnames=True)

print(f"✓ Found {len(frequent_itemsets):,} frequent itemsets")
print(f"  - Min support: 1%")
print(f"  - Support range: {frequent_itemsets['support'].min():.4f} to {frequent_itemsets['support'].max():.4f}")

# ══════════════════════════════════════════════════════════════
# STEP 6: GENERATE ASSOCIATION RULES
# ══════════════════════════════════════════════════════════════

print("\n[STEP 6] Generating association rules...")

# Generate rules
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.1)

# Calculate lift
rules['lift'] = rules['lift'].round(2)
rules['confidence'] = rules['confidence'].round(2)
rules['support'] = rules['support'].round(4)

print(f"✓ Generated {len(rules):,} association rules")

# ══════════════════════════════════════════════════════════════
# STEP 7: FILTER HIGH-QUALITY RULES
# ══════════════════════════════════════════════════════════════

print("\n[STEP 7] Filtering high-quality rules...")

# Filter rules: confidence > 50% and lift > 1.0
high_quality_rules = rules[(rules['confidence'] >= 0.5) & (rules['lift'] > 1.0)].copy()

# Sort by lift
high_quality_rules = high_quality_rules.sort_values('lift', ascending=False)

print(f"✓ Found {len(high_quality_rules):,} high-quality rules")
print(f"  - Confidence >= 50%")
print(f"  - Lift > 1.0")

# ══════════════════════════════════════════════════════════════
# STEP 8: FORMAT RULES FOR OUTPUT
# ══════════════════════════════════════════════════════════════

print("\n[STEP 8] Formatting rules...")

# Extract product names
product_map = dict(zip(df['product_id'], df['description']))

output_rules = []
for idx, rule in high_quality_rules.iterrows():
    antecedents = ', '.join([product_map.get(item, item) for item in rule['antecedents']])
    consequents = ', '.join([product_map.get(item, item) for item in rule['consequents']])
    
    output_rules.append({
        'Product_A': antecedents[:100],  # Truncate for readability
        'Product_B': consequents[:100],
        'Support': rule['support'],
        'Confidence': rule['confidence'],
        'Lift': rule['lift']
    })

output_df = pd.DataFrame(output_rules)

print(f"✓ Formatted {len(output_df):,} rules")

# ══════════════════════════════════════════════════════════════
# STEP 9: SAVE RESULTS
# ══════════════════════════════════════════════════════════════

# ... (Step 9: Save CSV - jo already hai) ...
output_path = 'data/processed/market_basket_rules.csv'
output_df.to_csv(output_path, index=False)
print(f"✓ Saved to: {output_path}")

# ✅ NEW: Add this block to save to SQL Server
print("\n[STEP 9.1] Saving to SQL Server for Power BI...")
try:
    from sqlalchemy import create_engine
    from sqlalchemy.types import NVARCHAR, Float
    import urllib
    
    params = urllib.parse.quote_plus(
        'Driver={ODBC Driver 17 for SQL Server};'
        f'Server={SERVER};'
        f'Database={DATABASE};'
        'Trusted_Connection=yes;'
        'Encrypt=no;'
    )
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

    # Create table in SQL Server
    output_df.to_sql(
        'market_basket_rules', 
        engine, 
        if_exists='replace',  # Replace agar pehle se hai toh
        index=False,
        dtype={
            'Product_A': NVARCHAR(255),
            'Product_B': NVARCHAR(255),
            'Support': Float(),
            'Confidence': Float(),
            'Lift': Float()
        }
    )
    print(f"✓ Table 'market_basket_rules' created in SQL Server!")
except Exception as e:
    print(f"✗ Error saving to SQL: {e}")

# ══════════════════════════════════════════════════════════════
# STEP 10: TOP INSIGHTS
# ══════════════════════════════════════════════════════════════

print("\n[STEP 10] Top 10 Product Associations:")

top_rules = output_df.head(10)
for idx, (_, rule) in enumerate(top_rules.iterrows(), 1):
    print(f"\n  {idx}. {rule['Product_A']}")
    print(f"     → {rule['Product_B']}")
    print(f"     Confidence: {rule['Confidence']*100:.1f}% | Lift: {rule['Lift']:.2f}x")

conn.close()

# ══════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════