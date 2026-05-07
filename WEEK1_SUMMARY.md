#  WEEK 1: DATA ENGINEERING & SCHEMA

## Overview
Week 1 focused on building a rock-solid data foundation. We transformed a messy raw Excel dataset into a high-performance **Star Schema** database in SQL Server.

## Technical Execution
- **Primary Script**: `python/data_cleaning.py` (which triggers `data_loader.py`)
- **Health Check**: `python/verify.py`
---

##  The Star Schema Architecture
We designed a 4-table structure optimized for speed and Power BI analysis:

### 1. FACT_SALES (The Transaction Hub)
- **Purpose**: Stores the actual sales numbers (Quantity, Price, Total).
- **Volume**: ~500,000+ clean records.
- **Key Columns**: `invoice_id`, `customer_id`, `product_id`, `invoice_date`.

### 2. DIM_CUSTOMER (Who?)
- **Purpose**: Unique details of ~4,000+ customers and their home countries.

### 3. DIM_PRODUCT (What?)
- **Purpose**: Descriptive names for every unique Stock Code in the inventory.

### 4. DIM_DATE (When?)
- **Purpose**: A time lookup table that allows us to see trends by Day, Month, Quarter, and Week.

---

##  Data Cleaning (The Quality Filter)
We removed **7.6% of raw data** to ensure our insights are 100% accurate:
1. **Removed Cancelled Orders**: Filtered out all invoices starting with 'C'.
2. **Fixed Customer IDs**: Dropped transactions with missing IDs.
3. **Valid Quantities Only**: Removed negative or zero quantity records.
4. **Price Correction**: Removed records with zero or negative unit prices.

---

##  Verification
We use the **`verify.py`** script to instantly confirm that:
- Tables are correctly created.
- Rows are successfully loaded.
- There are zero NULL values in critical columns.

---
**Status**: Week 1 Foundation is Complete and Verified.
