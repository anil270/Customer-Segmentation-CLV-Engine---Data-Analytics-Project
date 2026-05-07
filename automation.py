# ═══════════════════════════════════════════════════════════
# CONSUMER360: MASTER AUTOMATION SCRIPT
# Purpose: Run the entire pipeline with one click
# ═══════════════════════════════════════════════════════════

import subprocess
import sys

print("==================================================")
print("CONSUMER360: STARTING AUTOMATION PIPELINE")
print("==================================================")

def run_script(script_name):
    print(f"\n---> Starting: {script_name}")
    
    # Run the script and show its output directly on screen
    result = subprocess.run([sys.executable, f"python/{script_name}"])
    
    # If the script crashes, stop everything
    if result.returncode != 0:
        print(f"\n[FAIL] ERROR: {script_name} failed! Stopping pipeline.")
        sys.exit(1)
        
    print(f"[OK] {script_name} finished successfully!")

# ---------------------------------------------------------
# EXECUTE PIPELINE STEPS
# ---------------------------------------------------------

# STEP 1: Clean data and load into SQL Server
run_script("data_cleaning.py")

# STEP 2: Run Market Basket Analysis
run_script("market_basket.py")

# STEP 3: Run RFM Analysis (Including Predictive CLV)
run_script("rfm_analysis.py")

# STEP 4: Run Cohort Analysis
run_script("cohort_analysis.py")

# STEP 5: Live Database Verification
print("\n---> Starting LIVE Verification Check...")
run_script("verify.py")

print("\n==================================================")
print(" ALL DONE! PIPELINE COMPLETED SUCCESSFULLY ")
print("==================================================")
