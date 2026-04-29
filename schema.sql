-- ═══════════════════════════════════════════════════════════
-- CONSUMER360: STAR SCHEMA
-- Created: Week 1
-- Purpose: Define database structure for retail analytics
-- ═══════════════════════════════════════════════════════════

-- ─── TABLE 1: DIMENSION - CUSTOMER ──────────────────────────
-- Purpose: Store customer information
-- Rows: ~4,000 unique customers
-- Key: customer_id (Primary Key)

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id         INTEGER PRIMARY KEY,
    country             TEXT NOT NULL,
    first_purchase_date DATE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── TABLE 2: DIMENSION - PRODUCT ──────────────────────────
-- Purpose: Store product information
-- Rows: ~3,600 unique products
-- Key: product_id (Primary Key)

CREATE TABLE IF NOT EXISTS dim_product (
    product_id          TEXT PRIMARY KEY,
    description         TEXT NOT NULL,
    category            TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── TABLE 3: DIMENSION - DATE ─────────────────────────────
-- Purpose: Store date information for time-based analysis
-- Rows: 365 (one per day)
-- Key: date_id (Primary Key)

CREATE TABLE IF NOT EXISTS dim_date (
    date_id             DATE PRIMARY KEY,
    day                 INTEGER,
    month               INTEGER,
    quarter             INTEGER,
    year                INTEGER,
    week_of_year        INTEGER,
    day_of_week         TEXT,
    is_weekend          BOOLEAN
);

-- ─── TABLE 4: FACT - SALES ─────────────────────────────────
-- Purpose: Store transaction data (central fact table)
-- Rows: ~500,000 transactions
-- Keys: sale_id (Primary Key), customer_id/product_id/invoice_date (Foreign Keys)

CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id          TEXT NOT NULL,
    customer_id         INTEGER NOT NULL,
    product_id          TEXT NOT NULL,
    invoice_date        DATE NOT NULL,
    quantity            INTEGER NOT NULL,
    unit_price          REAL NOT NULL,
    total_amount        REAL NOT NULL,
    
    -- Foreign Key Constraints
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (invoice_date) REFERENCES dim_date(date_id)
);

-- ─── INDEXES FOR PERFORMANCE ───────────────────────────────
-- Purpose: Speed up queries on frequently filtered columns
-- These are the columns we'll use in WHERE and JOIN clauses

CREATE INDEX IF NOT EXISTS idx_fact_customer 
ON fact_sales(customer_id);

CREATE INDEX IF NOT EXISTS idx_fact_product 
ON fact_sales(product_id);

CREATE INDEX IF NOT EXISTS idx_fact_date 
ON fact_sales(invoice_date);

CREATE INDEX IF NOT EXISTS idx_fact_invoice 
ON fact_sales(invoice_id);

-- ═══════════════════════════════════════════════════════════
-- END OF SCHEMA
-- ═══════════════════════════════════════════════════════════