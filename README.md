# E-commerce Business Intelligence System

> **Mini-Projet Business Intelligence – MERN E-commerce**  
> Complete ETL pipeline and analytical dashboard for e-commerce data

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Deliverables](#deliverables)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🎯 Overview

This project implements a complete Business Intelligence system for an e-commerce MERN application, transforming operational MongoDB data into actionable insights through:

- **ETL Pipeline**: Python-based Extract, Transform, Load process
- **Data Warehouse**: PostgreSQL star schema design
- **Analytics Dashboard**: Power BI interactive visualizations
- **MERN Integration**: Dashboard embedded in web application

**Academic Context**: 5th Year Engineering Project  
**Technologies**: Python, MongoDB, PostgreSQL, Power BI, MERN Stack

---

## ✨ Features

### ETL Pipeline
- ✅ MongoDB data extraction (7 collections)
- ✅ Comprehensive data cleaning and validation
- ✅ Business metric calculation (Revenue, Profit, Margin)
- ✅ Date dimension with temporal attributes
- ✅ Star schema data warehouse loading
- ✅ Data quality checks and logging

### Data Warehouse
- ✅ Star schema with 1 fact table + 4 dimensions
- ✅ Optimized for analytical queries
- ✅ Indexed for performance
- ✅ Analytical views for common queries

### Power BI Dashboard
- 📊 Executive Overview (KPIs, trends)
- 🛍️ Sales Analysis (products, categories)
- 👥 Customer Analysis (segmentation, behavior)
- 🗺️ Geographical Analysis (regional performance)

### Integration
- ✅ React component for dashboard embedding
- ✅ Multiple integration options (Service, Public, PDF)
- ✅ Responsive design
- ✅ Authentication-ready

---

## 🏗️ Architecture

```
┌─────────────────┐
│   MongoDB       │  Operational Database
│  (E-commerce)   │  - users, products, orders
└────────┬────────┘  - order_items, payments
         │           - regions, categories
         │ Extract
         ▼
┌─────────────────┐
│  Python ETL     │  Data Processing
│   Pipeline      │  - Extraction
│                 │  - Transformation
└────────┬────────┘  - Loading
         │
         │ Load
         ▼
┌─────────────────┐
│  PostgreSQL     │  Data Warehouse
│  Data Warehouse │  Star Schema:
│                 │  - fact_sales
│                 │  - dim_date, dim_product
└────────┬────────┘  - dim_customer, dim_region
         │
         │ Connect
         ▼
┌─────────────────┐
│   Power BI      │  Analytics & Visualization
│   Dashboard     │  - DAX Measures
│                 │  - 4 Dashboard Pages
└────────┬────────┘  - Interactive Filters
         │
         │ Embed
         ▼
┌─────────────────┐
│  MERN App       │  Front-end Integration
│  (React)        │  - Dashboard Component
└─────────────────┘  - User Interface
```

---

## 📦 Prerequisites

### Required Software
- **Python**: 3.8 or higher
- **Docker**: For PostgreSQL
- **Power BI Desktop**: Free version
- **Node.js**: 14+ (for MERN integration)

### Optional
- **MongoDB**: Connection to existing MERN app database
- **Power BI Pro/Premium**: For Service integration

---

## 🚀 Installation

### Step 1: Clone Repository

```bash
cd c:\Users\mjarb\OneDrive\Bureau\DATA_BI
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Start PostgreSQL Data Warehouse

```bash
# Start Docker container
docker-compose up -d

# Verify PostgreSQL is running
docker ps

# Check logs
docker logs ecommerce_dw
```

The schema will be automatically created from `sql/schema.sql`.

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your MongoDB credentials
# MONGO_URI=mongodb://your-mongodb-connection-string
# MONGO_DB=your_database_name
```

### Step 5: Verify Installation

```bash
# Test PostgreSQL connection
docker exec -it ecommerce_dw psql -U bi_admin -d ecommerce_dw -c "SELECT version();"

# Test ETL modules (once MongoDB is ready)
python etl/config.py
```

---

## 💻 Usage

### Running the ETL Pipeline

#### Full Pipeline

```bash
# Run complete ETL process
cd c:\Users\mjarb\OneDrive\Bureau\DATA_BI
python etl/main.py
```

#### Partial Execution

```bash
# Extract only
python etl/main.py --extract-only

# Transform only
python etl/main.py --transform-only

# Load only
python etl/main.py --load-only
```

#### Skip Phases

```bash
# Skip extraction (use cached data)
python etl/main.py --skip-extract
```

### Monitoring

```bash
# View logs
cd logs
type etl_pipeline.log

# Monitor PostgreSQL
docker exec -it ecommerce_dw psql -U bi_admin -d ecommerce_dw

# Check row counts
ecommerce_dw=# SELECT COUNT(*) FROM fact_sales;
ecommerce_dw=# SELECT COUNT(*) FROM dim_product;
```

### Data Verification

```bash
# Run data quality checks
docker exec -it ecommerce_dw psql -U bi_admin -d ecommerce_dw -f sql/verify_data.sql
```

---

## 📁 Project Structure

```
DATA_BI/
├── etl/                          # ETL Pipeline
│   ├── __init__.py
│   ├── config.py                 # Configuration & logging
│   ├── extract.py                # MongoDB extraction
│   ├── transform.py              # Data transformation
│   ├── load.py                   # PostgreSQL loading
│   └── main.py                   # Pipeline orchestrator
│
├── sql/                          # SQL Scripts
│   ├── schema.sql                # Data warehouse DDL
│   └── verify_data.sql           # Quality checks
│
├── docs/                         # Documentation
│   ├── powerbi_guide.md          # Power BI tutorial
│   ├── mern_integration.md       # Integration guide
│   └── schema_diagram.png        # ER diagram (to generate)
│
├── powerbi/                      # Power BI Files
│   └── ecommerce_bi.pbix         # Dashboard file (to create)
│
├── logs/                         # Log Files
│   └── etl_pipeline.log          # ETL execution logs
│
├── docker-compose.yml            # PostgreSQL setup
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .env                          # Your configuration (create this)
└── README.md                     # This file
```

---

## 📚 Documentation

### Core Documentation
- **[Power BI Guide](docs/powerbi_guide.md)**: Step-by-step dashboard creation
- **[MERN Integration](docs/mern_integration.md)**: Web app integration
- **[Implementation Plan](../../.gemini/antigravity/brain/a360e7ff-2077-4303-b3a3-e2ec12787fcd/implementation_plan.md)**: Technical design

### Quick References

#### MongoDB Collections
- `users` - Customer data
- `products` - Product catalog
- `orders` - Order headers
- `order_items` - Order line items
- `payments` - Payment transactions
- `regions` - Geographic regions
- `categories` - Product categories

#### Star Schema Tables

**Fact Table**:
- `fact_sales` - Sales transactions with metrics

**Dimensions**:
- `dim_date` - Date dimension
- `dim_product` - Product dimension
- `dim_customer` - Customer dimension
- `dim_region` - Geographic dimension

#### Key Metrics Calculated
- **Revenue** = `price × quantity`
- **Profit** = `(price - cost) × quantity`
- **Margin %** = `(profit / revenue) × 100`
- **Average Basket** = `revenue / distinct orders`

---

## 📦 Deliverables

### Required Files

- [x] **ETL Python Scripts**: `etl/*.py` (fully commented)
- [x] **Data Warehouse Schema**: `sql/schema.sql`
- [ ] **Power BI Dashboard**: `powerbi/ecommerce_bi.pbix` (create using guide)
- [x] **Documentation**: `docs/*.md`
- [x] **Integration Code**: `docs/mern_integration.md`
- [ ] **ER Diagram**: Generate from Power BI or draw.io

### For Academic Submission

1. **Code Repository**: Complete project folder
2. **Documentation**: README + technical guides
3. **Dashboard File**: `.pbix` file
4. **Presentation**: PowerPoint/PDF slides
5. **Demo Video**: Screen recording of dashboard (optional)

---

## 🔧 Troubleshooting

### Docker Issues

**PostgreSQL won't start**:
```bash
# Check if port 5432 is already in use
netstat -ano | findstr :5432

# Stop and remove existing containers
docker-compose down -v
docker-compose up -d
```

### ETL Issues

**MongoDB connection failed**:
- Verify connection string in `.env`
- Check MongoDB is running
- Test connection: `mongo "your-connection-string"`

**Import errors**:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Power BI Issues

**Cannot connect to PostgreSQL**:
- Ensure Docker container is running
- Use connection: `localhost:5432`
- Database: `ecommerce_dw`
- User: `bi_admin`
- Password: `bi_password_2024`

**Relationships not detected**:
- Manually create in Model view
- Verify key columns match (date_id, product_id, etc.)

---

## 🎓 Academic Notes

### Project Highlights for Presentation

1. **Complete BI Pipeline**: End-to-end data flow
2. **Star Schema Design**: Industry-standard approach
3. **Business Metrics**: Real analytical value
4. **Modern Tech Stack**: Python, PostgreSQL, Power BI
5. **Production-Ready**: Logging, error handling, validation

### Suggested Presentation Structure

1. **Introduction** (2 min)
   - Context: E-commerce BI needs
   - Objectives

2. **Architecture** (5 min)
   - System diagram
   - Technology choices

3. **ETL Pipeline** (8 min)
   - Extraction process
   - Transformation logic
   - Business metrics
   - Data quality

4. **Data Warehouse** (5 min)
   - Star schema design
   - Dimension tables
   - Fact table

5. **Dashboard** (8 min)
   - Live demo
   - Key insights
   - Interactivity

6. **Integration** (3 min)
   - MERN integration
   - Deployment

7. **Conclusion** (2 min)
   - Results
   - Future work

---

## 📝 Next Steps

### When MongoDB is Ready

1. **Configure Connection**:
   ```bash
   # Edit .env file
   MONGO_URI=your_actual_connection_string
   MONGO_DB=your_database_name
   ```

2. **Run ETL Pipeline**:
   ```bash
   python etl/main.py
   ```

3. **Verify Data**:
   ```bash
   docker exec -it ecommerce_dw psql -U bi_admin -d ecommerce_dw -c "SELECT * FROM vw_sales_summary LIMIT 10;"
   ```

4. **Create Dashboard**:
   - Open Power BI Desktop
   - Follow `docs/powerbi_guide.md`
   - Save as `powerbi/ecommerce_bi.pbix`

5. **Integrate with MERN**:
   - Follow `docs/mern_integration.md`
   - Test in your application

---

## 📧 Support

For issues or questions:
1. Check logs: `logs/etl_pipeline.log`
2. Review documentation in `docs/`
3. Verify PostgreSQL: `docker logs ecommerce_dw`
4. Test connections in Python console

---

## 🎉 Conclusion

This project demonstrates a professional-grade BI system suitable for academic presentation and real-world application. The modular design allows for easy extension and maintenance.

**Good luck with your project defense! 🎓**

---

**Version**: 1.0.0  
**Date**: January 2026  
**Academic Level**: 5th Year Engineering  
**Technologies**: Python, MongoDB, PostgreSQL, Power BI, MERN
