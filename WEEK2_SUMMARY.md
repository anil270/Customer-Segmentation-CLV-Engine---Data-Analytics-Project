# WEEK 2: RFM ANALYSIS & MARKET BASKET — COMPLETE SUMMARY

## Overview
Week 2 focused on extracting business intelligence from the cleaned data by building advanced analytical models. The goal was to understand customer behavior and product relationships.

## Technical Execution
During this week, we worked on two primary analytical engines:
1. **RFM Analysis Engine**: `python/rfm_analysis.py`
2. **Market Basket Engine**: `python/market_basket.py`

These scripts process the cleaned data from Week 1 and generate predictive insights that are loaded back into the SQL Server database.

---

## Part 1: RFM Analysis

### What is RFM?
RFM stands for Recency, Frequency, Monetary. It is a proven marketing technique to segment customers based on their purchase behavior.

### How We Calculated RFM
1. **Raw Metrics**: Calculated Recency (days since last purchase), Frequency (total unique orders), and Monetary (total spend) for each customer.
2. **Scoring (1-5 Scale)**: Used `pd.qcut()` to divide customers into 5 equal buckets for each metric.
3. **Segmentation**: Combined scores to assign labels like Champions, Loyal, At Risk, and Hibernating.

### RFM Results (Actual Output)
- **Total customers analyzed**: 5,860
- **Recency range**: 27 to 760 days
- **Frequency range**: 1 to 391 purchases
- **Monetary range**: £2.90 to £597,336.11

#### Segment Distribution

| Segment           | Customers | %     | Avg Recency | Avg Frequency | Avg Monetary   | Total Revenue    |
|-------------------|-----------|-------|-------------|---------------|----------------|------------------|
| Price Sensitive   | 1,983     | 33.8% | 377 days    | 1.6           | £519.00        | £1,029,173.78    |
| Hibernating       | 1,075     | 18.3% | 118 days    | 5.5           | £2,153.01      | £2,314,488.25    |
| Promising         | 728       | 12.4% | 55 days     | 5.3           | £1,766.71      | £1,286,167.11    |
| Champions         | 454       | 7.7%  | 35 days     | 28.7          | £17,809.22     | £8,085,386.88    |
| **TOTAL**         | **5,860** | **100%** |          |               |                | **£17,324,932**  |

#### Key Insights from RFM
- **Insight 1**: Champions (7.7% customers) drive **46.7% of Revenue**. Action: VIP program and loyalty rewards.
- **Insight 2**: **Can't Lose Them** segment needs urgent action. High-value customers who have gone silent for 500+ days. Action: Immediate win-back campaigns.

---

## Part 2: Market Basket Analysis

### What is Market Basket Analysis?
Market Basket Analysis finds products that are frequently bought together using Association Rule Mining (Apriori/FP-Growth).

### How We Did It
1. **Transaction Matrix**: Created a matrix of invoices vs products (1 if present, 0 if not).
2. **FP-Growth Algorithm**: Used the `mlxtend` library to find frequent itemsets with a min support of 1-3%.
3. **Rule Generation**: Calculated Support, Confidence, and Lift for product pairs.

### Market Basket Results (Actual Output)
- **Total transactions analyzed**: 36,457
- **Unique products**: 4,630
- **High-quality rules**: 254 (Confidence >= 50%, Lift > 1.0)

#### Top Product Associations

| If Customer Buys | They Also Buy | Confidence | Lift |
|-----------------|---------------|------------|------|
| POPPY'S PLAYHOUSE LIVINGROOM | POPPY'S PLAYHOUSE BEDROOM | 83% | 54.82x |
| PINK SPOTTY CUP | BLUE SPOTTY CUP | 70% | 45.29x |
| WOODEN TREE CHRISTMAS SCANDINAVIAN | WOODEN STAR CHRISTMAS SCANDINAVIAN | 79% | 44.99x |

#### Key Insights from MBA
- **Insight 1**: Poppy's Playhouse Bundle Opportunity. All 3 playhouse items are bought together with 80%+ confidence. Action: Create a discounted bundle.
- **Insight 2**: Cross-Selling Engine. Use the 254 rules to power "Customers who bought X also bought Y" recommendations.

---

## Files Produced in Week 2

| File | Location | Description |
|------|----------|-------------|
| `rfm_analysis.py` | `python/` | Primary script for segmentation |
| `market_basket.py` | `python/` | Primary script for association rules |
| `rfm_segmentation.csv` | `data/processed/` | Exported metrics for all customers |
| `market_basket_rules.csv` | `data/processed/` | Exported association rules |
| `rfm_segmentation` (SQL) | SQL Server | Database table for Power BI |