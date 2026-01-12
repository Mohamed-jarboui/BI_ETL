-- E-commerce Data Warehouse Schema (Star Schema)
-- PostgreSQL 15+

-- Drop existing tables if they exist
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_region CASCADE;

-- ============================================
-- DIMENSION: dim_date
-- ============================================
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    week_of_year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT FALSE
);

-- Create index for common filters
CREATE INDEX idx_date_year ON dim_date(year);
CREATE INDEX idx_date_quarter ON dim_date(quarter);
CREATE INDEX idx_date_month ON dim_date(month);

-- ============================================
-- DIMENSION: dim_product
-- ============================================
CREATE TABLE dim_product (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2),
    brand VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Create index for category filtering
CREATE INDEX idx_product_category ON dim_product(category_name);

-- ============================================
-- DIMENSION: dim_customer
-- ============================================
CREATE TABLE dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    gender VARCHAR(20),
    registration_date DATE,
    customer_segment VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Create index for customer segment analysis
CREATE INDEX idx_customer_segment ON dim_customer(customer_segment);

-- ============================================
-- DIMENSION: dim_region
-- ============================================
CREATE TABLE dim_region (
    region_id VARCHAR(50) PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    continent VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Create index for regional analysis
CREATE INDEX idx_region_country ON dim_region(country);

-- ============================================
-- FACT TABLE: fact_sales
-- ============================================
CREATE TABLE fact_sales (
    sale_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    order_item_id VARCHAR(50) NOT NULL,
    date_id INTEGER NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    region_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    revenue DECIMAL(12,2) NOT NULL,
    cost_amount DECIMAL(12,2),
    profit DECIMAL(12,2),
    margin_pct DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
);

-- Create indexes for fact table performance
CREATE INDEX idx_fact_date ON fact_sales(date_id);
CREATE INDEX idx_fact_product ON fact_sales(product_id);
CREATE INDEX idx_fact_customer ON fact_sales(customer_id);
CREATE INDEX idx_fact_region ON fact_sales(region_id);
CREATE INDEX idx_fact_order ON fact_sales(order_id);

-- ============================================
-- VIEWS FOR ANALYSIS
-- ============================================

-- Sales Summary View
CREATE OR REPLACE VIEW vw_sales_summary AS
SELECT 
    d.year,
    d.quarter,
    d.month_name,
    p.category_name,
    r.region_name,
    r.country,
    COUNT(DISTINCT fs.order_id) as total_orders,
    SUM(fs.quantity) as total_quantity,
    SUM(fs.revenue) as total_revenue,
    SUM(fs.profit) as total_profit,
    AVG(fs.margin_pct) as avg_margin_pct,
    SUM(fs.revenue) / NULLIF(COUNT(DISTINCT fs.order_id), 0) as avg_basket_value
FROM fact_sales fs
JOIN dim_date d ON fs.date_id = d.date_id
JOIN dim_product p ON fs.product_id = p.product_id
JOIN dim_region r ON fs.region_id = r.region_id
GROUP BY d.year, d.quarter, d.month_name, p.category_name, r.region_name, r.country;

-- Top Products View
CREATE OR REPLACE VIEW vw_top_products AS
SELECT 
    p.product_id,
    p.product_name,
    p.category_name,
    SUM(fs.quantity) as total_quantity_sold,
    SUM(fs.revenue) as total_revenue,
    SUM(fs.profit) as total_profit,
    AVG(fs.margin_pct) as avg_margin_pct
FROM fact_sales fs
JOIN dim_product p ON fs.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category_name
ORDER BY total_revenue DESC;

-- Customer Analysis View
CREATE OR REPLACE VIEW vw_customer_analysis AS
SELECT 
    c.customer_id,
    c.full_name,
    c.customer_segment,
    r.region_name,
    COUNT(DISTINCT fs.order_id) as total_orders,
    SUM(fs.revenue) as total_revenue,
    SUM(fs.profit) as total_profit,
    SUM(fs.revenue) / NULLIF(COUNT(DISTINCT fs.order_id), 0) as avg_order_value
FROM fact_sales fs
JOIN dim_customer c ON fs.customer_id = c.customer_id
JOIN dim_region r ON fs.region_id = r.region_id
GROUP BY c.customer_id, c.full_name, c.customer_segment, r.region_name
ORDER BY total_revenue DESC;

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================
COMMENT ON TABLE dim_date IS 'Date dimension table for time-based analysis';
COMMENT ON TABLE dim_product IS 'Product dimension table with category and pricing information';
COMMENT ON TABLE dim_customer IS 'Customer dimension table with demographic information';
COMMENT ON TABLE dim_region IS 'Geographic dimension table for regional analysis';
COMMENT ON TABLE fact_sales IS 'Fact table containing sales transactions with metrics';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Data Warehouse schema created successfully!';
END $$;
