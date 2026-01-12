# Power BI Dashboard - Build Checklist

## ✅ COMPLETED
- [x] Connect to PostgreSQL (localhost, ecommerce_dw)
- [x] Load all 8 tables (5 core + 3 views)

---

## 📊 NEXT STEPS

### 1. CREATE RELATIONSHIPS (Model View)
Go to **Model View** (icon on left) and create these connections:

- [ ] `fact_sales.date_id` → `dim_date.date_id` (Many to One)
- [ ] `fact_sales.customer_id` → `dim_customer.customer_id` (Many to One)
- [ ] `fact_sales.product_id` → `dim_product.product_id` (Many to One)
- [ ] `fact_sales.region_id` → `dim_region.region_id` (Many to One)

**How**: Drag from fact_sales field → Drop on matching dim field

---

### 2. BUILD KEY METRICS (Report View)

Switch to **Report View**, then add these cards:

#### Row 1 - Financial KPIs
- [ ] **Card 1**: Total Revenue
  - Fields: `fact_sales.revenue` (sum)
  - Expected: ~$3.6M

- [ ] **Card 2**: Total Profit
  - Fields: `fact_sales.profit` (sum)
  - Expected: ~$922K

- [ ] **Card 3**: Average Margin
  - Fields: `fact_sales.margin_pct` (average)
  - Expected: ~25%

- [ ] **Card 4**: Total Transactions
  - Fields: `fact_sales.sale_id` (count)
  - Expected: 5,244

---

### 3. CREATE TREND CHARTS

#### Revenue Over Time (Line Chart)
- [ ] Visualization: Line Chart
- [ ] X-axis: `dim_date.date`
- [ ] Y-axis: `fact_sales.revenue` (sum)
- [ ] Legend: None

#### Revenue by Region (Bar Chart)
- [ ] Visualization: Clustered Bar Chart
- [ ] Y-axis: `dim_region.region_name`
- [ ] X-axis: `fact_sales.revenue` (sum)
- [ ] Sort: Descending by revenue

#### Top Categories (Column Chart)
- [ ] Visualization: Clustered Column Chart
- [ ] X-axis: `dim_product.category_name`
- [ ] Y-axis: `fact_sales.revenue` (sum)
- [ ] Sort: Descending by revenue

---

### 4. ADD INTERACTIVITY

#### Date Slicer
- [ ] Visualization: Slicer
- [ ] Field: `dim_date.year`
- [ ] Style: Dropdown or List

#### Region Filter
- [ ] Visualization: Slicer
- [ ] Field: `dim_region.region_name`
- [ ] Style: List with checkboxes

---

### 5. OPTIONAL ENHANCEMENTS

- [ ] Add dashboard title (Insert → Text Box)
- [ ] Apply a theme (View → Themes)
- [ ] Format card colors
- [ ] Add profit margin gauge chart
- [ ] Create customer table (top 10 by revenue)

---

### 6. SAVE & TEST

- [ ] Save file: `Ecommerce_Dashboard.pbix`
- [ ] Test filters work on all visuals
- [ ] Export to PDF for presentation

---

## 🎯 QUICK REFERENCE

**Views to Use** (Alternative to building from scratch):
- `vw_sales_summary` - Pre-aggregated metrics
- `vw_customer_analysis` - Customer insights
- `vw_top_products` - Best sellers

**Common Issues**:
- If visual shows error: Check relationships are active
- If numbers look wrong: Ensure aggregation is SUM not AVG
- If filter doesn't work: Check cross-filter direction

---

## 📸 EXPECTED RESULTS

**Total Revenue Card**: $3,612,837.83
**Top Region**: Sousse ($562K)
**Top Category**: Groceries ($458K)
**Date Range**: 2024-2025 data

