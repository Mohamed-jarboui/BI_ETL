# Quick Start Guide

## 1. Start PostgreSQL (REQUIRED)

```bash
cd c:\Users\mjarb\OneDrive\Bureau\DATA_BI
docker-compose up -d
```

**Verify it's running**:
```bash
docker ps
```

You should see `ecommerce_dw` container running.

---

## 2. Set Up Python Environment

```bash
# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt
```

---

## 3. Configure MongoDB Connection

When your MongoDB is ready:

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your MongoDB details:
   ```env
   MONGO_URI=mongodb://your-connection-string
   MONGO_DB=your_database_name
   ```

---

## 4. Run ETL Pipeline

```bash
# Make sure virtual environment is activated
# Make sure PostgreSQL Docker is running

python etl/main.py
```

**Monitor progress**: Check `logs/etl_pipeline.log`

---

## 5. Verify Data

```bash
# Check row counts
docker exec -it ecommerce_dw psql -U bi_admin -d ecommerce_dw -c "SELECT COUNT(*) FROM fact_sales;"

# Run full verification
docker exec -it ecommerce_dw psql -U bi_admin -d ecommerce_dw -f sql/verify_data.sql
```

---

## 6. Create Power BI Dashboard

1. Open **Power BI Desktop**
2. Follow the guide: `docs/powerbi_guide.md`
3. Connect to PostgreSQL:
   - Server: `localhost:5432`
   - Database: `ecommerce_dw`
   - User: `bi_admin`
   - Password: `bi_password_2024`

---

## 7. Integrate with MERN

Follow: `docs/mern_integration.md`

---

## Common Commands

### PostgreSQL

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker logs ecommerce_dw

# Connect to database
docker exec -it ecommerce_dw psql -U bi_admin -d ecommerce_dw
```

### ETL

```bash
# Full pipeline
python etl/main.py

# Extract only
python etl/main.py --extract-only

# View logs
type logs\etl_pipeline.log
```

---

## Troubleshooting

**Port 5432 already in use?**
```bash
netstat -ano | findstr :5432
docker-compose down -v
docker-compose up -d
```

**MongoDB connection error?**
- Check `.env` file
- Verify MongoDB is running
- Test connection string

**Python import errors?**
```bash
pip install --upgrade -r requirements.txt
```

---

## File Checklist

- [x] `docker-compose.yml` - PostgreSQL setup
- [x] `requirements.txt` - Python dependencies
- [x] `.env` - Your configuration (create from .env.example)
- [x] `etl/*.py` - ETL scripts
- [x] `sql/schema.sql` - Database schema
- [x] `docs/powerbi_guide.md` - Dashboard guide
- [ ] `powerbi/ecommerce_bi.pbix` - Your dashboard (to create)

---

**Need help?** Check `README.md` for detailed documentation!
