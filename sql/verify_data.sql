-- Data Quality Verification Queries
-- Run after ETL pipeline completes

\echo '\n=== DATA WAREHOUSE VERIFICATION ==='
\echo '==================================\n'

-- Row Counts
\echo '1. TABLE ROW COUNTS'
\echo '-------------------'
SELECT 'dim_date' as table_name, COUNT(*) as row_count FROM dim_date
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL
SELECT 'dim_region', COUNT(*) FROM dim_region
UNION ALL
SELECT 'fact_sales', COUNT(*) FROM fact_sales
ORDER BY table_name;

\echo '\n2. DATA QUALITY CHECKS'
\echo '----------------------'

-- Check for orphaned records
\echo 'Orphaned Sales (missing product):'
SELECT COUNT(*) as orphaned_product_count
FROM fact_sales fs
LEFT JOIN dim_product dp ON fs.product_id = dp.product_id
WHERE dp.product_id IS NULL;

\echo 'Orphaned Sales (missing customer):'
SELECT COUNT(*) as orphaned_customer_count
FROM fact_sales fs
LEFT JOIN dim_customer dc ON fs.customer_id = dc.customer_id
WHERE dc.customer_id IS NULL;

\echo 'Orphaned Sales (missing date):'
SELECT COUNT(*) as orphaned_date_count
FROM fact_sales fs
LEFT JOIN dim_date dd ON fs.date_id = dd.date_id
WHERE dd.date_id IS NULL;

\echo 'Orphaned Sales (missing region):'
SELECT COUNT(*) as orphaned_region_count
FROM fact_sales fs
LEFT JOIN dim_region dr ON fs.region_id = dr.region_id
WHERE dr.region_id IS NULL;

-- Check for invalid data
\echo '\n3. INVALID DATA CHECKS'
\echo '----------------------'

\echo 'Negative Revenue:'
SELECT COUNT(*) as negative_revenue_count
FROM fact_sales
WHERE revenue < 0;

\echo 'Zero or Negative Quantity:'
SELECT COUNT(*) as invalid_quantity_count
FROM fact_sales
WHERE quantity <= 0;

\echo 'Null Critical Fields:'
SELECT 
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) as null_order_id,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) as null_product_id,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_customer_id,
    SUM(CASE WHEN revenue IS NULL THEN 1 ELSE 0 END) as null_revenue
FROM fact_sales;

\echo '\n4. BUSINESS METRICS SUMMARY'
\echo '---------------------------'

SELECT 
    COUNT(DISTINCT order_id) as total_orders,
    COUNT(DISTINCT customer_id) as total_customers,
    COUNT(DISTINCT product_id) as total_products,
    SUM(quantity) as total_quantity_sold,
    ROUND(SUM(revenue)::numeric, 2) as total_revenue,
    ROUND(SUM(profit)::numeric, 2) as total_profit,
    ROUND(AVG(margin_pct)::numeric, 2) as avg_margin_pct,
    ROUND((SUM(revenue) / COUNT(DISTINCT order_id))::numeric, 2) as avg_basket_value
FROM fact_sales;

\echo '\n5. DATE RANGE'
\echo '-------------'

SELECT 
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    MAX(date) - MIN(date) as date_range_days
FROM dim_date
WHERE date_id IN (SELECT DISTINCT date_id FROM fact_sales);

\echo '\n6. TOP 5 PRODUCTS BY REVENUE'
\echo '----------------------------'

SELECT 
    dp.product_name,
    dp.category_name,
    SUM(fs.revenue) as total_revenue,
    SUM(fs.quantity) as total_quantity
FROM fact_sales fs
JOIN dim_product dp ON fs.product_id = dp.product_id
GROUP BY dp.product_name, dp.category_name
ORDER BY total_revenue DESC
LIMIT 5;

\echo '\n7. TOP 5 CUSTOMERS BY REVENUE'
\echo '-----------------------------'

SELECT 
    dc.full_name,
    dr.region_name,
    COUNT(DISTINCT fs.order_id) as total_orders,
    SUM(fs.revenue) as total_revenue
FROM fact_sales fs
JOIN dim_customer dc ON fs.customer_id = dc.customer_id
JOIN dim_region dr ON fs.region_id = dr.region_id
GROUP BY dc.full_name, dr.region_name
ORDER BY total_revenue DESC
LIMIT 5;

\echo '\n8. REVENUE BY REGION'
\echo '--------------------'

SELECT 
    dr.region_name,
    dr.country,
    COUNT(DISTINCT fs.order_id) as total_orders,
    SUM(fs.revenue) as total_revenue,
    ROUND(AVG(fs.margin_pct)::numeric, 2) as avg_margin_pct
FROM fact_sales fs
JOIN dim_region dr ON fs.region_id = dr.region_id
GROUP BY dr.region_name, dr.country
ORDER BY total_revenue DESC;

\echo '\n9. MONTHLY REVENUE TREND'
\echo '------------------------'

SELECT 
    dd.year,
    dd.month,
    dd.month_name,
    COUNT(DISTINCT fs.order_id) as orders,
    SUM(fs.revenue) as revenue,
    SUM(fs.profit) as profit
FROM fact_sales fs
JOIN dim_date dd ON fs.date_id = dd.date_id
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month
LIMIT 12;

\echo '\n=== VERIFICATION COMPLETE ===\n'
