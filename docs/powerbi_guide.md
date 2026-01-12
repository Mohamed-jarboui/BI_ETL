# Power BI Guide: E-commerce Business Intelligence Dashboard

## Table of Contents
1. [Connecting to PostgreSQL](#connecting-to-postgresql)
2. [DAX Measures](#dax-measures)
3. [Dashboard Pages](#dashboard-pages)
4. [Publishing & Integration](#publishing--integration)

---

## Connecting to PostgreSQL

### Step 1: Open Power BI Desktop

Launch Power BI Desktop (free version is sufficient for development)

### Step 2: Get Data from PostgreSQL

1. Click **Get Data** → **More...**
2. Search for **PostgreSQL database**
3. Click **Connect**

### Step 3: Enter Database Credentials

- **Server**: `localhost:5432`
- **Database**: `ecommerce_dw`
- Click **OK**

### Step 4: Authentication

- **User name**: `bi_admin`
- **Password**: `bi_password_2024`
- Click **Connect**

### Step 5: Select Tables

Select all 5 tables:
- ✅ fact_sales
- ✅ dim_date
- ✅ dim_product
- ✅ dim_customer
- ✅ dim_region

Click **Load** (use Import mode for best performance with small datasets)

### Step 6: Verify Relationships

Go to **Model** view and verify these relationships were auto-detected:

| From Table | From Column | To Table | To Column | Cardinality |
|------------|-------------|----------|-----------|-------------|
| fact_sales | date_id | dim_date | date_id | Many-to-One |
| fact_sales | product_id | dim_product | product_id | Many-to-One |
| fact_sales | customer_id | dim_customer | customer_id | Many-to-One |
| fact_sales | region_id | dim_region | region_id | Many-to-One |

---

## DAX Measures

Create a new table called **Measures** to organize all DAX measures.

### 1. Total Revenue

```dax
Total Revenue = SUM(fact_sales[revenue])
```

### 2. Total Profit

```dax
Total Profit = SUM(fact_sales[profit])
```

### 3. Total Quantity Sold

```dax
Total Quantity = SUM(fact_sales[quantity])
```

### 4. Total Orders

```dax
Total Orders = DISTINCTCOUNT(fact_sales[order_id])
```

### 5. Average Basket Value

```dax
Average Basket = 
DIVIDE(
    [Total Revenue],
    [Total Orders],
    0
)
```

**Format**: Currency, 2 decimals

### 6. Profit Margin %

```dax
Profit Margin % = 
DIVIDE(
    [Total Profit],
    [Total Revenue],
    0
) * 100
```

**Format**: Percentage, 2 decimals

### 7. Revenue by Product

```dax
Revenue by Product = 
CALCULATE(
    [Total Revenue],
    ALLEXCEPT(dim_product, dim_product[product_name])
)
```

### 8. Revenue by Region

```dax
Revenue by Region = 
CALCULATE(
    [Total Revenue],
    ALLEXCEPT(dim_region, dim_region[region_name])
)
```

### 9. YoY Revenue Growth % (Advanced)

```dax
YoY Revenue Growth % = 
VAR CurrentRevenue = [Total Revenue]
VAR PreviousRevenue = 
    CALCULATE(
        [Total Revenue],
        DATEADD(dim_date[date], -1, YEAR)
    )
RETURN
    DIVIDE(
        CurrentRevenue - PreviousRevenue,
        PreviousRevenue,
        0
    ) * 100
```

**Format**: Percentage, 1 decimal

### 10. Month-over-Month Growth %

```dax
MoM Growth % = 
VAR CurrentRevenue = [Total Revenue]
VAR PreviousRevenue = 
    CALCULATE(
        [Total Revenue],
        DATEADD(dim_date[date], -1, MONTH)
    )
RETURN
    DIVIDE(
        CurrentRevenue - PreviousRevenue,
        PreviousRevenue,
        0
    ) * 100
```

**Format**: Percentage, 1 decimal

### 11. Average Order Value (AOV)

```dax
AOV = 
DIVIDE(
    SUM(fact_sales[revenue]),
    DISTINCTCOUNT(fact_sales[order_id]),
    0
)
```

**Format**: Currency, 2 decimals

### 12. Customer Count

```dax
Total Customers = DISTINCTCOUNT(fact_sales[customer_id])
```

---

## Dashboard Pages

### Page 1: Executive Overview 📊

**Purpose**: High-level KPIs and trends for executives

**Visuals**:

1. **KPI Cards** (Top row)
   - Total Revenue (`[Total Revenue]`)
   - Total Profit (`[Total Profit]`)
   - Total Orders (`[Total Orders]`)
   - Profit Margin % (`[Profit Margin %]`)

2. **Line Chart**: Revenue & Profit Trend
   - X-axis: `dim_date[date]` (by Month)
   - Y-axis: `[Total Revenue]`, `[Total Profit]`
   - Legend: Measure names

3. **Column Chart**: Top 5 Categories by Revenue
   - X-axis: `dim_product[category_name]`
   - Y-axis: `[Total Revenue]`
   - Sort: Descending by revenue
   - Top N filter: 5

4. **Donut Chart**: Revenue Distribution by Region
   - Values: `[Total Revenue]`
   - Legend: `dim_region[region_name]`

5. **Slicers**
   - `dim_date[year]`
   - `dim_date[quarter]`
   - `dim_region[region_name]`

**Design**: Use a clean, professional theme with consistent colors

---

### Page 2: Sales Analysis 🛍️

**Purpose**: Detailed product and category analysis

**Visuals**:

1. **Table**: Product Performance
   - Columns:
     - `dim_product[product_name]`
     - `dim_product[category_name]`
     - `[Total Revenue]`
     - `[Total Profit]`
     - `[Total Quantity]`
     - `[Profit Margin %]`
   - Sort by: Total Revenue (descending)

2. **Bar Chart**: Top 10 Products by Revenue
   - Y-axis: `dim_product[product_name]`
   - X-axis: `[Total Revenue]`
   - Sort: Top 10
   - Data bars for easy comparison

3. **Donut/Pie Chart**: Revenue by Category
   - Values: `[Total Revenue]`
   - Legend: `dim_product[category_name]`

4. **Tree Map**: Products by Category
   - Group: `dim_product[category_name]`
   - Values: `[Total Revenue]`
   - Size: Revenue (larger = more revenue)

5. **Line Chart**: Monthly Sales Trend
   - X-axis: `dim_date[month_name]`
   - Y-axis: `[Total Revenue]`

---

### Page 3: Customer Analysis 👥

**Purpose**: Customer behavior and segmentation insights

**Visuals**:

1. **KPI Cards**
   - Total Customers (`[Total Customers]`)
   - Average Order Value (`[AOV]`)
   - Average Basket (`[Average Basket]`)

2. **Table**: Top 20 Customers
   - Columns:
     - `dim_customer[full_name]`
     - `dim_region[region_name]`
     - `[Total Orders]`
     - `[Total Revenue]`
     - `[AOV]`
   - Sort by: Total Revenue (descending)
   - Top N filter: 20

3. **Bar Chart**: Customers by Region
   - Y-axis: `dim_region[region_name]`
   - X-axis: `[Total Customers]`

4. **Scatter Plot**: Customer Value Analysis
   - X-axis: `[Total Orders]`
   - Y-axis: `[Total Revenue]`
   - Values: `dim_customer[full_name]`
   - Tooltip: Customer name, region

5. **Column Chart**: Customer Acquisition Over Time
   - X-axis: `dim_customer[registration_date]` (by Month)
   - Y-axis: Count of customers

---

### Page 4: Geographical Analysis 🗺️

**Purpose**: Regional performance insights

**Visuals**:

1. **Map Visual**: Sales by Region
   - Location: `dim_region[country]`
   - Bubble size: `[Total Revenue]`
   - Bubble color: `[Profit Margin %]`

2. **Table**: Regional Performance Summary
   - Columns:
     - `dim_region[region_name]`
     - `dim_region[country]`
     - `[Total Revenue]`
     - `[Total Profit]`
     - `[Profit Margin %]`
     - `[Total Orders]`
   - Conditional formatting on Profit Margin %

3. **Bar Chart**: Top Regions by Revenue
   - Y-axis: `dim_region[region_name]`
   - X-axis: `[Total Revenue]`

4. **Column Chart**: Profit Margin by Region
   - X-axis: `dim_region[region_name]`
   - Y-axis: `[Profit Margin %]`
   - Reference line: Average margin

---

## Design Best Practices

### Color Scheme
- **Primary**: Professional blue (#0078D4)
- **Secondary**: Accent orange (#FF8C00)
- **Success**: Green (#107C10)
- **Warning**: Yellow (#FFB900)
- **Error**: Red (#D13438)

### Typography
- **Title**: Segoe UI Bold, 18pt
- **Subtitle**: Segoe UI Semibold, 14pt
- **Body**: Segoe UI, 11pt

### General Guidelines
1. **Consistency**: Use the same colors and fonts across all pages
2. **White Space**: Don't overcrowd visuals
3. **Hierarchy**: Most important metrics at the top/left
4. **Interactivity**: Enable cross-filtering between visuals
5. **Tooltips**: Add custom tooltips with additional context
6. **Mobile Layout**: Design for mobile viewing (optional)

---

## Publishing & Integration

### Option 1: Power BI Service (Requires Pro/Premium)

1. **Publish to Power BI Service**
   - Click **Publish** in Power BI Desktop
   - Sign in to Power BI Service
   - Select workspace
   - Wait for upload to complete

2. **Configure Data Refresh**
   - Go to workspace → Settings
   - Configure gateway (if needed)
   - Set refresh schedule (daily recommended)

3. **Generate Embed Code**
   - Open report in Power BI Service
   - Click **File** → **Embed report** → **Website or portal**
   - Copy the iframe code

4. **Integrate in MERN Application**
   - See `docs/mern_integration.md` for React component code

### Option 2: Export to PDF (Free Alternative)

Since you have Power BI Desktop Free:

1. **Export to PDF**
   - Open the dashboard
   - Click **File** → **Export to PDF**
   - Save the PDF

2. **Share PDF**
   - Share PDF with stakeholders
   - Update regularly and re-export

3. **Alternative: Publish to Web (Public)**
   - **⚠ WARNING**: This makes your data publicly accessible
   - Click **File** → **Publish to Web**
   - Generate public link
   - Use iframe in your MERN app

---

## Verification Checklist

- [ ] All 5 tables imported successfully
- [ ] Relationships verified (4 relationships, all Many-to-One)
- [ ] All DAX measures created and formatted
- [ ] Page 1: Executive Overview completed
- [ ] Page 2: Sales Analysis completed
- [ ] Page 3: Customer Analysis completed
- [ ] Page 4: Geographical Analysis completed
- [ ] All slicers working correctly
- [ ] Cross-filtering enabled between visuals
- [ ] Mobile layout configured (optional)
- [ ] Dashboard saved as `.pbix` file
- [ ] Dashboard tested with real data

---

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to PostgreSQL

**Solution**:
1. Ensure Docker container is running: `docker ps`
2. Check PostgreSQL is accepting connections: `docker logs ecommerce_dw`
3. Verify credentials in Power BI match `.env` file

### Missing Data

**Problem**: Tables are empty

**Solution**:
1. Run ETL pipeline: `python etl/main.py`
2. Verify data in PostgreSQL: `docker exec -it ecommerce_dw psql -U bi_admin -d ecommerce_dw -c "SELECT COUNT(*) FROM fact_sales;"`

### Relationship Errors

**Problem**: Relationships not auto-detected

**Solution**:
1. Manually create relationships in Model view
2. Ensure cardinality is set to Many-to-One
3. Set cross-filter direction to Single

---

## Next Steps

1. Complete the dashboard following this guide
2. Test with real data from MongoDB
3. Export to PDF or publish to Power BI Service
4. Integrate into MERN application (see `docs/mern_integration.md`)
5. Prepare presentation materials for academic defense

**Good luck with your BI project! 🎓**
