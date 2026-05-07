#  WEEK 2: RFM ANALYSIS & MARKET BASKET

## Overview
Week 2 added the "Intelligence" layer. We built two analytical engines in Python to understand exactly who our customers are and which products they love to buy together.

## Technical Execution
- **RFM Engine**: `python/rfm_analysis.py`
- **MBA Engine**: `python/market_basket.py`
---
## Part 1: RFM Analysis (Segmentation)
We segmented **5,860 unique customers** based on three metrics:
1. **Recency**: How many days since their last order?
## Part 1: RFM Analysis & Predictive CLV

### What is RFM?
RFM stands for Recency, Frequency, Monetary. It is a proven marketing technique to segment customers based on their purchase behavior.

### Predictive CLV Modeling
Using the **`lifetimes`** library, we implemented predictive modeling (BG/NBD and Gamma-Gamma models) to estimate the **future value** of each customer for the next 12 months. This allows the business to focus on high-potential customers before they even spend.

---

## Part 2: Cohort Analysis (Retention)

### What is Cohort Analysis?
It tracks how many customers from a specific "Join Month" (Cohort) continue to buy in subsequent months.

### Key Insights:
- **Retention Rates**: We can now see exactly when customers stop buying (e.g., "Month 3 Churn") and target them with retention offers.
- **Acquisition Quality**: Compares which months brought in the most loyal customers.

---

## Part 3: Market Basket Analysis (Association)
We analyzed over **36,000 transactions** to find product relationships. Using the **FP-Growth** algorithm, we generated **254 high-quality rules**.

### Examples of Insights:
- **Product Bundling**: If a customer buys "Poppy's Playhouse Bedroom," they are 83% likely to buy the "Living Room" set.
- **Cross-Selling**: We identified 254 specific "Frequently Bought Together" pairs to power recommendation engines.
---
## Outputs Generated
- **`rfm_segmentation`**: Uploaded to SQL Server for live Power BI dashboards.
- **`market_basket_rules`**: Uploaded to SQL Server for cross-selling analysis.
- **Processed CSVs**: Stored in `data/processed/` for offline review.
---
**Status**: Analytical Models are Live and Feeding Data to SQL.
