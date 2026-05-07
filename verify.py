# ═══════════════════════════════════════════════════════════
# CONSUMER360: PIPELINE VERIFICATION
# Purpose: Check SQL Server to ensure all data is loaded
# ═══════════════════════════════════════════════════════════

import pyodbc
from datetime import datetime

print("==================================================")
print(f"  PIPELINE HEALTH CHECK | {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
print("==================================================")

try:
    conn = pyodbc.connect(r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-94L3J1Q\SQLEXPRESS;DATABASE=Consumer360;Trusted_Connection=yes;")
    cursor = conn.cursor()
    
    tables = ["fact_sales", "dim_customer", "rfm_segmentation", "market_basket_rules", "cohort_analysis"]
    all_good = True

    for t in tables:
        try:
            count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"[OK]   {t:<20} : {count:,} records" if count > 0 else f"[FAIL] {t:<20} : 0 records (BLANK!)")
            if count == 0: all_good = False
        except:
            print(f"[FAIL] {t:<20} : MISSING OR ERROR")
            all_good = False

    print("-" * 50)
    print("[SUCCESS] Pipeline is PERFECT! All tables are filled." if all_good else "[WARNING] Some tables are empty/missing!")
    print("==================================================")

except Exception as e:
    print(f"[FAIL] Database connection failed! {e}")
