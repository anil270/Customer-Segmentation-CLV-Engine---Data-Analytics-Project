-- ═══════════════════════════════════════════════════════════
-- CONSUMER360: WEEK 1 - TEST QUERIES
-- Purpose: Verify data quality and schema correctness
-- ═══════════════════════════════════════════════════════════

-- ─── QUERY 1: TOTAL SALES BY CUSTOMER ──────────────────────
-- Purpose: See top customers by revenue
-- Expected: Should run in <2 seconds
-- Result: Top 10 customers with their revenue

SELECT 
    c.customer_id,
    c.country,
    COUNT(DISTINCT f.invoice_id) as total_invoices,
    SUM(f.total_amount) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_order_value
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_id, c.country
ORDER BY total_revenue DESC
LIMIT 10;

-- ─── QUERY 2: MONTHLY SALES TREND ──────────────────────────
-- Purpose: See how sales changed over time
-- Expected: Should show monthly revenue progression
-- Result: Month-by-month revenue with customer count

SELECT 
    d.year,
    d.month,
    SUM(f.total_amount) as monthly_revenue,
    COUNT(DISTINCT f.customer_id) as unique_customers,
    COUNT(DISTINCT f.invoice_id) as total_orders,
    ROUND(AVG(f.total_amount), 2) as avg_order_value
FROM fact_sales f
JOIN dim_date d ON f.invoice_date = d.date_id
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- ─── QUERY 3: TOP PRODUCTS BY REVENUE ──────────────────────
-- Purpose: See which products generate most revenue
-- Expected: Should show top 20 products
-- Result: Product details with sales metrics

SELECT 
    p.product_id,
    p.description,
    COUNT(*) as times_sold,
    SUM(f.quantity) as total_quantity_sold,
    SUM(f.total_amount) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_sale_value
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.description
ORDER BY total_revenue DESC
LIMIT 20;

-- ─── QUERY 4: REVENUE BY COUNTRY ───────────────────────────
-- Purpose: See which countries generate most revenue
-- Expected: UK should be #1
-- Result: Country-wise revenue breakdown

SELECT 
    c.country,
    COUNT(DISTINCT c.customer_id) as unique_customers,
    COUNT(DISTINCT f.invoice_id) as total_orders,
    SUM(f.total_amount) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_order_value
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.country
ORDER BY total_revenue DESC;

-- ─── QUERY 5: CUSTOMER COHORT ANALYSIS ─────────────────────
-- Purpose: See how many customers joined each month
-- Expected: Should show customer acquisition over time
-- Result: Cohort month with customer count and revenue

SELECT 
    STRFTIME('%Y-%m', c.first_purchase_date) as cohort_month,
    COUNT(DISTINCT c.customer_id) as customers_acquired,
    SUM(f.total_amount) as cohort_revenue
FROM dim_customer c
LEFT JOIN fact_sales f ON c.customer_id = f.customer_id
GROUP BY cohort_month
ORDER BY cohort_month;

-- ─── QUERY 6: DATA QUALITY CHECK ───────────────────────────
-- Purpose: Verify no data issues
-- Expected: All NULL counts should be 0

SELECT 
    'fact_sales' as table_name,
    COUNT(*) as total_rows,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_customer_id,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) as null_product_id,
    SUM(CASE WHEN invoice_date IS NULL THEN 1 ELSE 0 END) as null_invoice_date,
    SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END) as null_total_amount,
    SUM(CASE WHEN total_amount <= 0 THEN 1 ELSE 0 END) as negative_amounts
FROM fact_sales;

-- ─── QUERY 7: DUPLICATE INVOICE CHECK ──────────────────────
-- Purpose: Check for duplicate invoices
-- Expected: Should be 0 (each invoice_id should be unique)

SELECT 
    invoice_id,
    COUNT(*) as count
FROM fact_sales
GROUP BY invoice_id
HAVING COUNT(*) > 1
ORDER BY count DESC;

-- ─── QUERY 8: SCHEMA VERIFICATION ──────────────────────────
-- Purpose: Verify all tables exist and have data
-- Expected: All 4 tables should have rows

SELECT 'dim_customer' as table_name, COUNT(*) as row_count FROM dim_customer
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date
UNION ALL
SELECT 'fact_sales', COUNT(*) FROM fact_sales;