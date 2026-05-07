# ═══════════════════════════════════════════════════════════
# CONSUMER360: MARKET BASKET ANALYSIS
# Purpose: Find products frequently bought together
# ═══════════════════════════════════════════════════════════

import pandas as pd
import urllib.parse
from sqlalchemy import create_engine
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import warnings

# Hide annoying warnings
warnings.filterwarnings("ignore")
print("Starting Market Basket Analysis...")

# 1. Connect & Load Data
print("Loading transaction data...")
SERVER = r"DESKTOP-94L3J1Q\SQLEXPRESS"
DATABASE = "Consumer360"
params = urllib.parse.quote_plus(f"Driver={{ODBC Driver 17 for SQL Server}};Server={SERVER};Database={DATABASE};Trusted_Connection=yes;Encrypt=no;")
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

query = """
SELECT f.invoice_id, p.description 
FROM fact_sales f JOIN dim_product p ON f.product_id = p.product_id
"""
df = pd.read_sql(query, engine).dropna(subset=['description'])

# 2. Group into Baskets
print("Grouping products into baskets...")
baskets = df.groupby('invoice_id')['description'].apply(list).values

# 3. Create Matrix & Run FP-Growth
print("Running FP-Growth Algorithm (finding patterns)...")
te = TransactionEncoder()
basket_matrix = pd.DataFrame(te.fit(baskets).transform(baskets), columns=te.columns_)

frequent_items = fpgrowth(basket_matrix, min_support=0.01, use_colnames=True)
rules = association_rules(frequent_items, metric="confidence", min_threshold=0.1)

# 4. Filter & Format Rules
print("Filtering strong rules...")
rules = rules[(rules['confidence'] >= 0.5) & (rules['lift'] > 1.0)].sort_values('lift', ascending=False)

# Make it readable (convert frozensets to strings)
rules['Product_A'] = rules['antecedents'].apply(lambda x: ", ".join(list(x))[:250])
rules['Product_B'] = rules['consequents'].apply(lambda x: ", ".join(list(x))[:250])

results_df = rules[['Product_A', 'Product_B', 'support', 'confidence', 'lift']].copy()
results_df[['support', 'confidence', 'lift']] = results_df[['support', 'confidence', 'lift']].round(3)

# 5. Save Results
print("Saving results to CSV and SQL Server...")
results_df.to_csv('data/processed/market_basket_rules.csv', index=False)
results_df.to_sql("market_basket_rules", engine, if_exists="replace", index=False)

print(f"\nFound {len(results_df)} strong product combinations.")
print("\nTop 5 Most Frequently Bought Together Products:")
print(results_df.head(5).to_string(index=False))

print("\nMarket Basket Analysis Complete!")
