"""
End-to-end test: seed MongoDB, run the full ETL, check the warehouse.

Needs running MongoDB and PostgreSQL (with sql/schema.sql applied), so it only
runs when RUN_INTEGRATION=1. CI starts both as service containers.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="set RUN_INTEGRATION=1")


@pytest.fixture(scope="module")
def warehouse():
    subprocess.run([sys.executable, "scripts/seed_mongo.py", "--orders", "500"], cwd=ROOT, check=True)

    from etl.config import Config
    from etl.main import ETLPipeline

    assert ETLPipeline().run()
    engine = create_engine(Config().PG_CONNECTION_STRING)
    yield engine
    engine.dispose()


def scalar(engine, sql):
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar()


def test_tables_are_loaded(warehouse):
    assert scalar(warehouse, "SELECT COUNT(*) FROM dim_product") == 180
    assert scalar(warehouse, "SELECT COUNT(*) FROM dim_customer") == 420
    assert scalar(warehouse, "SELECT COUNT(*) FROM dim_region") == 8
    assert scalar(warehouse, "SELECT COUNT(*) FROM fact_sales") > 0


def test_no_orphan_sales(warehouse):
    assert scalar(warehouse, """
        SELECT COUNT(*) FROM fact_sales fs
        LEFT JOIN dim_product p ON fs.product_id = p.product_id
        LEFT JOIN dim_customer c ON fs.customer_id = c.customer_id
        LEFT JOIN dim_date d ON fs.date_id = d.date_id
        WHERE p.product_id IS NULL OR c.customer_id IS NULL OR d.date_id IS NULL
    """) == 0


def test_analytical_views_work(warehouse):
    assert scalar(warehouse, "SELECT COUNT(*) FROM vw_sales_summary") > 0
    assert scalar(warehouse, "SELECT COUNT(*) FROM vw_top_products") > 0
