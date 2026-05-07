# ═══════════════════════════════════════════════════════════
# CONSUMER360: RFM & CLV ANALYSIS
# Purpose: Segment customers and predict future value
# ═══════════════════════════════════════════════════════════

import pandas as pd
import urllib.parse
from sqlalchemy import create_engine
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data
import warnings

# Hide annoying warnings
warnings.filterwarnings("ignore")
print("Starting RFM & CLV Analysis...")

# 1. Connect to Database & Load Data
print("Loading transaction data...")
SERVER = r"DESKTOP-94L3J1Q\SQLEXPRESS"
DATABASE = "Consumer360"
params = urllib.parse.quote_plus(f"Driver={{ODBC Driver 17 for SQL Server}};Server={SERVER};Database={DATABASE};Trusted_Connection=yes;Encrypt=no;")
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

query = """
SELECT f.customer_id, f.invoice_id, f.invoice_date, f.total_amount, c.country
FROM fact_sales f JOIN dim_customer c ON f.customer_id = c.customer_id
"""
df = pd.read_sql(query, engine)
df['invoice_date'] = pd.to_datetime(df['invoice_date'])

# 2. Calculate RFM Metrics
print("Calculating Recency, Frequency, and Monetary values...")
ref_date = pd.to_datetime("2011-12-31")

rfm = df.groupby("customer_id").agg({
    "invoice_date": "max",     
    "invoice_id": "nunique",   
    "total_amount": "sum",     
    "country": "first"         
}).reset_index()

rfm.columns = ["customer_id", "last_purchase_date", "frequency", "monetary", "country"]
rfm["recency"] = (ref_date - rfm["last_purchase_date"]).dt.days

# 3. Score Customers (1-5 Scale)
print("Assigning RFM scores...")
rfm["r_score"] = pd.qcut(rfm["recency"].rank(method="first"), q=5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

# 4. Define Segments
print("Categorizing customers...")
def get_segment(r, f, m):
    if r == 5 and f == 5 and m == 5: return "Champions"
    if r == 5 and f >= 4 and m >= 4: return "Loyal Customers"
    if r >= 4 and f == 5 and m == 5: return "Potential Loyalist"
    if r == 1 and f == 1 and m == 1: return "Lost"
    if r == 1 and f >= 4 and m >= 4: return "Can't Lose Them"
    if r >= 4 and f == 1 and m == 1: return "Recent Users"
    if r >= 4 and f >= 3 and m >= 3: return "Promising"
    if r == 2 and f >= 3 and m >= 3: return "Needs Attention"
    if r >= 3 and f == 2 and m == 2: return "About To Sleep"
    if r >= 3 and f >= 2 and m >= 2: return "Hibernating"
    return "Price Sensitive"

rfm["segment"] = rfm.apply(lambda row: get_segment(row["r_score"], row["f_score"], row["m_score"]), axis=1)

# 5. Predictive CLV Modeling
print("Calculating Predictive CLV...")
try:
    summary = summary_data_from_transaction_data(df, 'customer_id', 'invoice_date', 'total_amount', observation_period_end=ref_date)
    summary = summary[summary['frequency'] > 0] # Models need repeat customers
    
    bgf = BetaGeoFitter(penalizer_coef=0.0)
    bgf.fit(summary['frequency'], summary['recency'], summary['T'])
    
    ggf = GammaGammaFitter(penalizer_coef=0.0)
    ggf.fit(summary['frequency'], summary['monetary_value'])
    
    summary['predicted_clv'] = ggf.customer_lifetime_value(
        bgf, summary['frequency'], summary['recency'], summary['T'], summary['monetary_value'], time=12, discount_rate=0.01
    )
    
    rfm = rfm.merge(summary[['predicted_clv']], on="customer_id", how="left")
    print("SUCCESS: Predictive CLV calculated!")
except Exception as e:
    print(f"WARNING: Could not calculate CLV: {e}")

rfm["predicted_clv"] = rfm.get("predicted_clv", pd.Series(0, index=rfm.index)).fillna(0).round(2)
rfm = rfm.sort_values("monetary", ascending=False)

# 6. Save Results
print("Saving results to CSV and SQL Server...")
rfm.to_csv("data/processed/rfm_segmentation.csv", index=False)
rfm.to_sql("rfm_segmentation", engine, if_exists="replace", index=False)

print("\nSegment Distribution Summary:")
print(rfm["segment"].value_counts().to_string())
print("\nRFM Analysis Complete!")
