#  Project Report: Consumer360 - Customer Intelligence Engine

## 1. Executive Summary
**Project Name**: Consumer360  
**Objective**: To transform raw e-commerce transaction data into a sophisticated, automated analytics product that identifies high-value customers, predicts future revenue, and tracks customer retention.

The project has successfully delivered an end-to-end pipeline that handles everything from data cleaning to advanced predictive modeling and live business dashboards.

---

## 2. Business Case
A mid-sized e-commerce retailer was struggling with generic marketing and high customer churn. **Consumer360** was developed to:
- Identify **"Champions"** (VIPs) for premium loyalty programs.
- Flag **"Churn Risks"** (Hibernating) customers for urgent retention efforts.
- Forecast **Future Revenue** to optimize marketing spend.
- Identify **Product Associations** for better cross-selling.

---

## 3. Technical Architecture
The project follows a modular, "human-readable" procedural design:

1.  **ETL (Extract, Transform, Load)**: Python/Pandas cleans 1M+ rows of Excel data and pushes it into a **SQL Server Star Schema** (Fact Sales, Dim Customer, Dim Product, Dim Date).
2.  **Analytical Logic**:
    - **RFM Analysis**: 1-5 scoring for Recency, Frequency, and Monetary metrics.
    - **Predictive CLV**: Utilizing the `lifetimes` library to predict the expected value of each customer for the next 12 months.
    - **Cohort Analysis**: Monthly retention tracking grouped by customer acquisition month.
    - **Market Basket Analysis**: FP-Growth algorithm to find product associations (e.g., "People who bought X also bought Y").
3.  **Orchestration & Automation**:
    - **`automation.py`**: A master script that coordinates all sub-processes.
    - **Windows Task Scheduler**: Configured to run the entire pipeline every Sunday at 11:00 PM.
    - **`verify.py`**: A live health-check script that validates database integrity after every run.

---

## 4. Key Performance Indicators (KPIs)
- **Total Revenue**: £15.97M (Historical)
- **Predicted Future Revenue**: £6.83M (Next 12 Months)
- **Unique Customers**: 5,860
- **Total Transactions**: 775,137
- **Retention Goal**: Focus on Month 3 churn where retention typically drops by 25%.

---

## 5. Strategic Insights
- **Geographic Risk**: 82% of revenue is UK-based. Recommendation: Expand marketing in high-value countries like the **Netherlands** and **Germany**.
- **Timing Intelligence**: Thursday is the peak sales day. Recommendation: Launch major promotions on Wednesday afternoons.
- **Cross-Selling**: 254 high-quality product association rules have been identified to power "Frequently Bought Together" sections.

---

## 6. Project Status
**Current State**: FULLY OPERATIONAL & AUTOMATED  
**Stability**: Verified with automated health checks.  
**Maintenance**: Zero manual intervention required for weekly updates.

---
**Report Prepared By**: Anil Kumar
**Date**: May 2026
