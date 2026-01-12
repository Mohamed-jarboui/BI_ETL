# Power BI - Pre-Built Views Guide

## 📊 What You Can Build from Each View

---

## 1️⃣ **vw_sales_summary** - Time & Location Analytics

### 📋 Contains:
- `year`, `quarter`, `month_name` - Time dimensions
- `category_name` - Product category
- `region_name`, `country` - Geography
- `total_orders` - Number of transactions
- `total_quantity` - Items sold
- `total_revenue` - Sales revenue
- `total_profit` - Profit amount
- `avg_margin_pct` - Profit margin %
- `avg_basket_value` - Average order size

### 🎯 KPIs You Can Build:

#### Cards (Instant Metrics)
1. **Overall Performance**
   - Total Revenue: Sum of `total_revenue`
   - Total Profit: Sum of `total_profit`
   - Average Margin: Avg of `avg_margin_pct`
   - Total Orders: Sum of `total_orders`

2. **Average Metrics**
   - Average Basket Value: Avg of `avg_basket_value`
   - Items per Order: `total_quantity / total_orders`

#### Charts
1. **Revenue Trend by Time**
   - Line Chart: X = `month_name`, Y = `total_revenue`
   - Or: X = `year` + `quarter`, Y = `total_revenue`

2. **Revenue by Region**
   - Bar Chart: Y = `region_name`, X = `total_revenue`
   - Map: Geography = `region_name`, Size = `total_revenue`

3. **Revenue by Category**
   - Column Chart: X = `category_name`, Y = `total_revenue`
   - Pie Chart: Legend = `category_name`, Values = `total_revenue`

4. **Quarterly Performance**
   - Table: `year`, `quarter`, `total_revenue`, `total_profit`, `avg_margin_pct`

5. **Margin Analysis**
   - Scatter Chart: X = `total_revenue`, Y = `avg_margin_pct`, Legend = `category_name`

---

## 2️⃣ **vw_customer_analysis** - Customer Insights

### 📋 Contains:
- `customer_id`, `full_name` - Customer identity
- `customer_segment` - Customer type/role
- `region_name` - Where they're from
- `total_orders` - How many times they ordered
- `total_revenue` - Revenue from this customer
- `total_profit` - Profit from this customer
- `avg_order_value` - Average spend per order

### 🎯 KPIs You Can Build:

#### Cards
1. **Customer Metrics**
   - Total Customers: Count distinct `customer_id`
   - Average Order Value: Avg of `avg_order_value`
   - Revenue per Customer: Sum `total_revenue` / Count `customer_id`

#### Charts
1. **Top 10 Customers by Revenue**
   - Table: `full_name`, `total_orders`, `total_revenue`, `total_profit`
   - Sort: Descending by `total_revenue`
   - Filter: Top 10

2. **Customer Segmentation**
   - Pie Chart: Legend = `customer_segment`, Values = Count of customers
   - Or: Values = `total_revenue` to see revenue by segment

3. **Regional Customer Distribution**
   - Bar Chart: Y = `region_name`, X = Count of `customer_id`
   - Add `total_revenue` as data label

4. **Customer Value Matrix**
   - Scatter Chart: 
     - X = `total_orders` (frequency)
     - Y = `avg_order_value` (value)
     - Size = `total_revenue`
     - Legend = `customer_segment`

5. **High-Value Customers Table**
   - Matrix: 
     - Rows = `full_name`, `region_name`
     - Values = `total_revenue`, `total_profit`, `total_orders`
   - Filter: Where `total_revenue` > threshold

---

## 3️⃣ **vw_top_products** - Product Performance

### 📋 Contains:
- `product_id`, `product_name` - Product identity
- `category_name` - Product category
- `total_quantity_sold` - Units sold
- `total_revenue` - Revenue generated
- `total_profit` - Profit generated
- `avg_margin_pct` - Profit margin %

### 🎯 KPIs You Can Build:

#### Cards
1. **Product Performance**
   - Total Products: Count of `product_id`
   - Best Seller Units: Max of `total_quantity_sold`
   - Average Product Margin: Avg of `avg_margin_pct`

#### Charts
1. **Top 20 Products by Revenue**
   - Bar Chart: Y = `product_name`, X = `total_revenue`
   - Filter: Top 20
   - Color: By `category_name`

2. **Category Performance**
   - Column Chart: X = `category_name`, Y = `total_revenue`
   - Add `total_profit` as second metric (dual axis)

3. **Product Profitability Matrix**
   - Scatter Chart:
     - X = `total_revenue` (sales)
     - Y = `avg_margin_pct` (profitability)
     - Size = `total_quantity_sold`
     - Legend = `category_name`
   - Identifies: High revenue/High margin products

4. **Best Sellers Table**
   - Table: `product_name`, `category_name`, `total_quantity_sold`, `total_revenue`, `total_profit`
   - Sort: By `total_quantity_sold` descending

5. **Category Comparison**
   - Treemap: 
     - Category = `category_name`
     - Values = `total_revenue`
     - Details = `product_name`

---

## 🎨 RECOMMENDED DASHBOARD LAYOUTS

### **Dashboard 1: Executive Summary**
Use: **vw_sales_summary**
- Row 1: 4 Cards (Revenue, Profit, Margin, Orders)
- Row 2: Revenue Trend (Line Chart)
- Row 3: Revenue by Region (Bar) + Revenue by Category (Pie)
- Filters: Year, Quarter

### **Dashboard 2: Customer Analytics**
Use: **vw_customer_analysis**
- Row 1: Cards (Total Customers, Avg Order Value, Revenue/Customer)
- Row 2: Top 10 Customers (Table)
- Row 3: Customer Segments (Pie) + Regional Distribution (Bar)
- Row 4: Customer Value Matrix (Scatter)

### **Dashboard 3: Product Performance**
Use: **vw_top_products**
- Row 1: Cards (Total Products, Best Seller, Avg Margin)
- Row 2: Top 20 Products (Bar Chart)
- Row 3: Profitability Matrix (Scatter) + Category Performance (Column)
- Row 4: Best Sellers Table

---

## ⚡ QUICK WIN - Use These Views FIRST

**Why?** These views are pre-aggregated, so:
- ✅ Faster performance
- ✅ No relationship setup needed
- ✅ Simpler to build
- ✅ Already have calculated metrics

**Start with vw_sales_summary** to build your first complete dashboard in 10 minutes!

Then add customer and product pages for a complete analytics suite.

