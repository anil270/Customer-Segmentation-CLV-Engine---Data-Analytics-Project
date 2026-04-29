# WEEK 3: VISUALIZATION & BUSINESS INTELLIGENCE — COMPLETE SUMMARY

## Overview
Week 3 focused on transforming analytical data into high-impact visuals across two platforms: a comprehensive Power BI Dashboard and an interactive HTML5 Presentation Deck.

## Technical Execution
- **Dashboards**: `powerbi/Consumer360_Dashboard.pbix`
- **Presentation**: `presentation.html` (Custom built with Chart.js)
- **Data Source**: Live SQL Server connection to `Consumer360` DB.

---

## Part 1: Interactive HTML Presentation Insights

Our custom-built presentation provides a high-level executive summary of the project's success.

### 1. Key Performance Indicators (KPIs)
- **Total Revenue**: £15.97M
- **Unique Customers**: 5,924
- **Total Transactions**: 775,137
- **Total Products**: 4,645
- **Avg Order Value**: £20.61
- **Global Reach**: 38 Countries

### 2. Revenue Trends & Intelligence
- **Monthly Trend**: Significant peaks identified in **November 2010** and **November 2011**, with both months exceeding **£1.1M** in sales due to holiday demand.
- **Day-of-Week Performance**: **Thursday** emerged as the highest-grossing day, while Saturday showed the lowest activity.

### 3. Geographic Performance
- **UK Dominance**: Generates **82.7%** of total revenue (£13.2M) from 5,396 customers.
- **High-Value International**: The **Netherlands** stands out with an incredible **£23,320 average spend per customer** (Total: £536K from only 23 customers).
- **Growth Potential**: EIRE and Germany show strong repeat order patterns.

### 4. Product Intelligence (Top 5 by Revenue)
1. **Regency Cakestand 3 Tier**: £273K (1,309 buyers)
2. **White Hanging Heart T-Light**: £244K (1,489 buyers)
3. **Jumbo Bag Red White Spotty**: £167K (975 buyers)
4. **Assorted Colour Bird Ornament**: £123K (1,005 buyers)
5. **Party Bunting**: £103K (893 buyers)

---

## Part 2: Power BI Dashboard Architecture

The Power BI report provides the deep-dive analytical capability for the marketing team.

### 1. Multi-Page Deep Dive
- **Overview Page**: Real-time KPI tiles and monthly trend analysis.
- **RFM Analysis Page**: Scatter plots showing customer health and segment distribution.
- **Market Basket Page**: Heatmaps showing product associations and cross-selling lift metrics.
- **Geographic Page**: Global revenue heatmap with country-specific drill-downs.

### 2. Automated Pipeline Visualization
The dashboard is the final step in a fully automated architecture:
**Excel Source** (1M+ rows) → **Data Cleaning** (Python/Pandas) → **SQL Server** (Star Schema) → **RFM/MBA Analysis** → **Power BI Dashboard**.

---

## Files Produced in Week 3

| File | Location | Description |
|------|----------|-------------|
| `Consumer360_Dashboard.pbix` | `powerbi/` | Interactive Power BI Report |
| `presentation.html` | root | Executive HTML Presentation Deck |
| `WEEK3_SUMMARY.md` | `doc/` | Final Visualization Documentation |
