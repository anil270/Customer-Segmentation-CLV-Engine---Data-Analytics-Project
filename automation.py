# ═══════════════════════════════════════════════════════════
# CONSUMER360: MASTER AUTOMATION SCRIPT
# Purpose: Run the entire pipeline with one click
# ═══════════════════════════════════════════════════════════

import subprocess, sys

print("==================================================")
print("   CONSUMER360: STARTING AUTOMATION PIPELINE")
print("==================================================")

# Sequence of all pipeline steps
pipeline_steps = [
    "data_cleaning.py",
    "market_basket.py",
    "rfm_analysis.py",
    "cohort_analysis.py",
    "verify.py"
]

# Execute each script in order
for script in pipeline_steps:
    print(f"\n---> Running: {script}")
    if subprocess.run([sys.executable, f"python/{script}"]).returncode != 0:
        print(f"\n[FAIL] ERROR: '{script}' crashed! Pipeline stopped.")
        sys.exit(1)
    print(f"[OK] {script} finished successfully!")

print("\n==================================================")
print("  ALL DONE! PIPELINE COMPLETED SUCCESSFULLY ")
print("==================================================")
