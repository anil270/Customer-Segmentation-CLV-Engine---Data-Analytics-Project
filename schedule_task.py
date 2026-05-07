# ═══════════════════════════════════════════════════════════
# CONSUMER360: TASK SCHEDULER
# Purpose: Automatically run the pipeline every Sunday night
# ═══════════════════════════════════════════════════════════

import os, subprocess, sys

print("Consumer360 Weekly Automation...")

ROOT = r"f:\Zaalima Data Analyst Internship\Consumer360"
SCRIPT = os.path.join(ROOT, "python", "automation.py")
TASK_NAME = "Consumer360_Weekly_Pipeline"

print(f"Scheduling '{TASK_NAME}' to run every Sunday at 11:00 PM...")

try:
    cmd = f'schtasks /Create /SC WEEKLY /D SUN /TN "{TASK_NAME}" /TR "{sys.executable} \\"{SCRIPT}\\"" /ST 23:00 /F'
    res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
    if res.returncode == 0:
        print("\n[SUCCESS] Task scheduled! Pipeline will now run automatically.")
    else:
        print(f"\n[ERROR] Failed: {res.stderr.strip()}")
        print(f"[MANUAL FIX] Open Task Scheduler -> Create Basic Task '{TASK_NAME}' -> Sunday 11 PM -> Start Program '{sys.executable}' '{SCRIPT}'")

except Exception as e:
    print(f"\n[ERROR] System Error: {e}")

print("Setup Complete!")
