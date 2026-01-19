# 🎉 E-commerce BI System - GitHub Repository

**Live at**: https://github.com/Mohamed-jarboui/dataanal

---

## 📦 What's Included

### **Complete BI Infrastructure**
✅ **24 files** | **3,748 lines of code** | **Production-ready**

---

## 📂 Repository Structure

```
dataanal/
├── 📊 ETL Pipeline (Python)
│   ├── etl/main.py           - Orchestration engine
│   ├── etl/extract.py        - MongoDB extraction
│   ├── etl/transform.py      - Star schema transformation
│   ├── etl/load.py           - PostgreSQL loading
│   └── etl/config.py         - Configuration management
│
├── 🗄️ Data Warehouse (PostgreSQL)
│   ├── sql/schema.sql        - Star schema DDL
│   └── sql/verify_data.sql   - Data quality checks
│
├── 📊 Power BI Integration
│   ├── docs/powerbi_guide.md      - Dashboard creation guide
│   ├── POWERBI_CHECKLIST.md       - Step-by-step tasks
│   └── POWERBI_VIEWS_GUIDE.md     - Pre-built views reference
│
├── 🔄 MERN Integration
│   ├── docs/mern_integration.md   - Embedding guide
│   └── DEMO_WORKFLOW.md           - End-to-end demo
│
├── 📚 Documentation
│   ├── README.md             - Complete project overview
│   ├── QUICKSTART.md         - Fast setup (5 min)
│   └── HEALTH_CHECK.md       - System verification
│
├── 🐳 Docker & Setup
│   ├── docker-compose.yml    - PostgreSQL container
│   ├── setup.bat             - Automated setup
│   └── run_etl.bat           - ETL execution
│
└── ⚙️ Configuration
    ├── requirements.txt      - Python dependencies
    ├── .env.example          - Environment template
    └── .gitignore            - Git exclusions
```

---

## 🚀 Key Features

### **1. ETL Pipeline**
- ✅ MongoDB Atlas → PostgreSQL sync
- ✅ Business ID-based joins (userId, productId, orderId)
- ✅ Automatic schema detection
- ✅ Data quality validation
- ✅ Referential integrity checks

### **2. Data Warehouse**
- ✅ Star schema (1 fact + 4 dimensions)
- ✅ Pre-built analytical views
- ✅ 5,248 sales transactions
- ✅ $3.6M revenue tracked
- ✅ 420 customers, 180 products, 8 regions

### **3. Power BI Ready**
- ✅ Connection guides
- ✅ Dashboard templates
- ✅ Pre-aggregated views
- ✅ KPI calculations

### **4. Complete Documentation**
- ✅ Academic presentation materials
- ✅ End-to-end demo workflow
- ✅ System health checks
- ✅ Troubleshooting guides

---

## 🎯 Quick Start

```powershell
# Clone the repository
git clone https://github.com/Mohamed-jarboui/dataanal.git
cd dataanal

# Setup (automated)
.\setup.bat

# Run ETL
.\run_etl.bat

# Connect Power BI to localhost:5432
```

**Full instructions**: See `QUICKSTART.md`

---

## 📊 Current Data Warehouse Status

| Metric | Value |
|--------|-------|
| **Total Sales** | 5,248 transactions |
| **Total Revenue** | $3,614,480.62 |
| **Total Profit** | $922,256.99 |
| **Average Margin** | 25.22% |
| **Date Range** | 2024-03-01 to 2026-01-12 |
| **Customers** | 420 unique |
| **Products** | 180 items |
| **Regions** | 8 locations |

---

## 🎓 Academic Project Highlights

### **Architecture**
- ✅ OLTP (MongoDB) vs OLAP (PostgreSQL) separation
- ✅ Batch ETL processing
- ✅ Star schema for analytical queries
- ✅ Docker containerization

### **Technologies Used**
- **Backend**: Python 3.13, Pandas, SQLAlchemy
- **Databases**: MongoDB Atlas, PostgreSQL 15
- **BI**: Power BI Desktop
- **DevOps**: Docker, Git, Windows Task Scheduler

### **Business Intelligence**
- ✅ Revenue trends analysis
- ✅ Regional performance tracking
- ✅ Product category insights
- ✅ Customer segmentation

---

## 🔄 Data Flow Demonstration

```
MERN App → MongoDB Atlas → ETL Pipeline → PostgreSQL → Power BI
   ✓           ✓              ✓             ✓           ✓
```

**See `DEMO_WORKFLOW.md` for live demonstration guide**

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Complete project overview |
| `QUICKSTART.md` | 5-minute setup guide |
| `HEALTH_CHECK.md` | System verification results |
| `DEMO_WORKFLOW.md` | End-to-end demo script |
| `POWERBI_CHECKLIST.md` | Dashboard building steps |
| `POWERBI_VIEWS_GUIDE.md` | Pre-built views reference |
| `docs/powerbi_guide.md` | Detailed Power BI instructions |
| `docs/mern_integration.md` | React embedding guide |

---

## 🎉 Project Status: **COMPLETE & PRODUCTION-READY**

✅ All core features implemented  
✅ End-to-end testing successful  
✅ Documentation comprehensive  
✅ Demo workflow verified  
✅ Code pushed to GitHub  

---

## 👨‍💻 Author

**Mohamed Jarboui**  
GitHub: [@Mohamed-jarboui](https://github.com/Mohamed-jarboui)  
Project: E-commerce Business Intelligence System

---

## 📅 Last Updated

2026-01-12 23:45 CET

---

**🌟 Star this repo if you found it useful!**
