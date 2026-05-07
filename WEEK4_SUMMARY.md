#  WEEK 4: AUTOMATION & ORCHESTRATION

## Overview
Week 4 was the final step: Operationalization. We moved from manual script running to a "Set it and Forget it" automated system.

## Technical Execution
- **The Orchestrator**: `python/automation.py`
- **The Scheduler**: `python/schedule_task.py`
- **Verification**: Integrated `verify.py` as a final automated step.

---

##  The Automation Pipeline
We unified the entire project into a single command. When `automation.py` runs, it executes the following steps in a perfect sequence:
1. **Clean & Load**: Wipes old data and inserts fresh transactions into SQL Server.
2. **RFM Analysis**: Recalculates all customer segments live.
3. **MBA Analysis**: Updates product association rules live.
4. **Live Verification**: Checks the database and prints a health report to the screen.

---

##  Automated Scheduling
We implemented a system that requires **Zero Human Interaction**:
- **Frequency**: Every Sunday.
- **Time**: 11:00 PM.
- **Mechanism**: Windows Task Scheduler.
- **Result**: Every Monday morning, business leaders wake up to fresh, updated dashboards without lifting a finger.

---

##  Final Handoff Summary
This project has delivered:
- **Speed**: Bulk-loading logic ensures data is pushed to SQL Server in seconds.
- **Readability**: Code is written in a simple procedural style for easy maintenance.
- **Reliability**: Integrated health checks ensure that data is always present and accurate.

---
**Status: PROJECT FULLY COMPLETED, AUTOMATED & HANDED OVER.**
