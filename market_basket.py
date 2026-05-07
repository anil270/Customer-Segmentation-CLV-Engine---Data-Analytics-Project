# ═══════════════════════════════════════════════════════════
# CONSUMER360: WEEK 2 - MARKET BASKET ANALYSIS
# Purpose: Find products frequently bought together
# ═══════════════════════════════════════════════════════════

import pandas as pd
import pyodbc
import urllib
from sqlalchemy import create_engine
from sqlalchemy.types import NVARCHAR, Float
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

print("Starting Market Basket Analysis...")

# 1. Connect to SQL Server
print("Connecting to SQL Server...")
SERVER = r"DESKTOP-94L3J1Q\SQLEXPRESS"
DATABASE = "Consumer360"

conn_str = f"Driver={{ODBC Driver 17 for SQL Server}};Server={SERVER};Database={DATABASE};Trusted_Connection=yes;Encrypt=no;"
conn = pyodbc.connect(conn_str)

# 2. Load the transaction data from SQL Server
print("Loading transaction data from database...")
query = """
SELECT 
    f.invoice_id, 
    p.description 
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
"""
import warnings
warnings.filterwarnings("ignore", message=".*pandas only supports SQLAlchemy connectable.*")
df = pd.read_sql(query, conn)
print(f"Loaded {len(df)} items.")

# 3. Group items by Invoice to create "Shopping Baskets"
print("Grouping products into shopping baskets...")
df = df.dropna(subset=['description'])
baskets = df.groupby('invoice_id')['description'].apply(list).values
print(f"Total number of transactions (baskets): {len(baskets)}")

# 4. Convert baskets into a True/False matrix (required by the algorithm)
print("Converting baskets for the algorithm...")
te = TransactionEncoder()
te_array = te.fit(baskets).transform(baskets)
basket_matrix = pd.DataFrame(te_array, columns=te.columns_)

# 5. Find frequent item combinations
print("Finding frequent items (this might take a moment)...")
frequent_items = fpgrowth(basket_matrix, min_support=0.01, use_colnames=True)

# 6. Generate rules (If customer buys A -> they will likely buy B)
print("Generating rules...")
rules = association_rules(frequent_items, metric="confidence", min_threshold=0.1)

# Keep only strong rules (Confidence >= 50% and Lift > 1.0)
strong_rules = rules[(rules['confidence'] >= 0.5) & (rules['lift'] > 1.0)].copy()
strong_rules = strong_rules.sort_values('lift', ascending=False)

# 7. Format the output to be easily readable
print("Formatting the final results...")
formatted_rules = []

for index, row in strong_rules.iterrows():
    product_a = ", ".join(list(row['antecedents']))
    product_b = ", ".join(list(row['consequents']))
    
    formatted_rules.append({
        'Product_A': product_a[:250], # Truncate if too long
        'Product_B': product_b[:250],
        'Support': round(row['support'], 4),
        'Confidence': round(row['confidence'], 2),
        'Lift': round(row['lift'], 2)
    })

results_df = pd.DataFrame(formatted_rules)
print(f"Found {len(results_df)} strong product combinations.")

# 8. Save results to CSV
output_path = 'data/processed/market_basket_rules.csv'
print(f"Saving results to {output_path}...")
results_df.to_csv(output_path, index=False)

# 9. Save results back to SQL Server
print("Saving results to SQL Server...")
params = urllib.parse.quote_plus(conn_str)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

results_df.to_sql(
    "market_basket_rules", 
    engine, 
    if_exists="replace", 
    index=False,
    dtype={
        "Product_A": NVARCHAR(255),
        "Product_B": NVARCHAR(255),
        "Support": Float(),
        "Confidence": Float(),
        "Lift": Float()
    }
)
print("Table 'market_basket_rules' updated in SQL Server!")

conn.close()

# 10. Show top 5 insights
print("\nTop 5 Most Frequently Bought Together Products:")
print(results_df.head(5).to_string(index=False))

print("\nMarket Basket Analysis Complete!")
