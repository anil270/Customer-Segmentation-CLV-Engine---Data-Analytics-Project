# ═══════════════════════════════════════════════════════════
# CONSUMER360: WEEK 4 - SCHEDULING SCRIPT
# Purpose: Schedule automation script to run every Sunday 11 PM
# ═══════════════════════════════════════════════════════════

import subprocess
import os
import sys

# Correct Absolute Paths for your system
PROJECT_ROOT = r"f:\Zaalima Data Analyst Internship\Consumer360"
SCRIPT_PATH = os.path.join(PROJECT_ROOT, "python", "automation.py")
PYTHON_EXE = sys.executable  # Automatically gets your python path

print("="*70)
print("CONSUMER360: AUTOMATED TASK SCHEDULER SETUP")
print("="*70)

def setup_windows_task():
    """
    Automatically creates a Windows Scheduled Task using schtasks command
    """
    task_name = "Consumer360_Weekly_Pipeline"
    
    # Command to run: python.exe "path/to/automation.py"
    # Scheduled for Every Sunday (SUN) at 23:00 (11 PM)
    command = f'schtasks /Create /SC WEEKLY /D SUN /TN "{task_name}" /TR "{PYTHON_EXE} \\"{SCRIPT_PATH}\\"" /ST 23:00 /F'

    print(f"\n[STEP 1] Creating Windows Task: {task_name}")
    try:
        # Run the command to create the task
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("SUCCESS: Task scheduled successfully!")
            print("   - Run Frequency: Every Sunday")
            print("   - Time: 11:00 PM")
            print("   - Script: automation.py")
        else:
            print(f"ERROR: Could not create task. {result.stderr}")
            print("\n[Alternative] Please follow manual steps below:")
            print_manual_steps()
    except Exception as e:
        print(f"Exception occurred: {e}")

def print_manual_steps():
    print("\n[MANUAL WINDOWS SETUP]")
    print("1. Open Task Scheduler (taskschd.msc)")
    print("2. Create Basic Task -> Name: 'Consumer360 Weekly Update'")
    print("3. Trigger: Weekly -> Sunday -> 11:00 PM")
    print("4. Action: Start a program")
    print(f"   - Program: {PYTHON_EXE}")
    print(f"   - Arguments: \"{SCRIPT_PATH}\"")
    print(f"   - Start in: {PROJECT_ROOT}")

if __name__ == "__main__":
    # Check if we are on Windows
    if os.name == 'nt':
        setup_windows_task()
    else:
        print("\n[MAC/LINUX SETUP]")
        print("Run 'crontab -e' and add:")
        print(f"0 23 * * 0 cd {PROJECT_ROOT} && {PYTHON_EXE} {SCRIPT_PATH}")

    print("\n" + "="*70)
    print("SETUP COMPLETE")
    print("="*70 + "\n")
