-- ═══════════════════════════════════════════════════════════
-- CONSUMER360: DATABASE SCHEMA
-- Purpose: Creates the clean Star Schema tables for the project
-- ═══════════════════════════════════════════════════════════

-- 1. Reset Database (Drop child first)
DROP TABLE IF EXISTS dbo.fact_sales;
DROP TABLE IF EXISTS dbo.dim_customer;
DROP TABLE IF EXISTS dbo.dim_product;
DROP TABLE IF EXISTS dbo.dim_date;

-- 2. Create Dimensions (Lookups)
CREATE TABLE dbo.dim_customer (
    customer_id INT PRIMARY KEY, country NVARCHAR(100), 
    first_purchase_date DATE, created_at DATETIME2 DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.dim_product (
    product_id NVARCHAR(50) PRIMARY KEY, description NVARCHAR(400), 
    category NVARCHAR(100), created_at DATETIME2 DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.dim_date (
    date_id DATE PRIMARY KEY, day INT, month INT, quarter INT, year INT, 
    week_of_year INT, day_of_week NVARCHAR(20), is_weekend BIT
);

-- 3. Create Fact Table (Sales)
CREATE TABLE dbo.fact_sales (
    sale_id INT IDENTITY(1,1) PRIMARY KEY,
    invoice_id NVARCHAR(50) NOT NULL,
    customer_id INT FOREIGN KEY REFERENCES dbo.dim_customer(customer_id),
    product_id NVARCHAR(50) FOREIGN KEY REFERENCES dbo.dim_product(product_id),
    invoice_date DATE FOREIGN KEY REFERENCES dbo.dim_date(date_id),
    quantity INT, unit_price DECIMAL(18,2), total_amount DECIMAL(18,2)
);

-- 4. Create Indexes for Dashboard Speed
CREATE INDEX idx_customer ON dbo.fact_sales(customer_id);
CREATE INDEX idx_product  ON dbo.fact_sales(product_id);
CREATE INDEX idx_date     ON dbo.fact_sales(invoice_date);
