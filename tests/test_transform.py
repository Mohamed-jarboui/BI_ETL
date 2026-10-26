"""
Unit tests for the transformation step, run on the generated demo dataset.
No database is needed: the data goes straight from the generator into DataFrames,
the same shape the extract step produces.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from etl.config import mask_uri  # noqa: E402
from etl.transform import DataTransformer  # noqa: E402
from seed_mongo import generate_dataset  # noqa: E402


@pytest.fixture(scope="module")
def raw():
    return generate_dataset(seed=1, n_users=80, n_products=40, n_orders=300)


@pytest.fixture(scope="module")
def data(raw):
    return {name: pd.DataFrame(docs) for name, docs in raw.items()}


@pytest.fixture(scope="module")
def result(data):
    return DataTransformer().transform_all(data)


# ---------- Demo data generator ----------

def test_generator_is_reproducible():
    assert generate_dataset(seed=3, n_orders=50) == generate_dataset(seed=3, n_orders=50)


def test_generated_references_are_consistent(raw):
    order_ids = {o["orderId"] for o in raw["orders"]}
    product_ids = {p["productId"] for p in raw["products"]}
    user_ids = {u["userId"] for u in raw["users"]}
    assert all(i["orderId"] in order_ids for i in raw["orderitems"])
    assert all(i["productId"] in product_ids for i in raw["orderitems"])
    assert all(o["userId"] in user_ids for o in raw["orders"])


# ---------- Dimensions ----------

def test_dimension_sizes(result, raw):
    dims, _ = result
    assert len(dims["dim_product"]) == len(raw["products"])
    assert len(dims["dim_customer"]) == len(raw["users"])
    assert len(dims["dim_region"]) == len(raw["regions"])


def test_dimension_keys_are_unique(result):
    dims, _ = result
    for table, key in [("dim_date", "date_id"), ("dim_product", "product_id"),
                       ("dim_customer", "customer_id"), ("dim_region", "region_id")]:
        assert dims[table][key].is_unique, table


def test_products_get_their_category_name(result):
    dims, _ = result
    assert (dims["dim_product"]["category_name"] != "Uncategorized").all()


def test_date_dimension_attributes(result):
    d = result[0]["dim_date"].iloc[0]
    assert d["date_id"] == d["date"].year * 10000 + d["date"].month * 100 + d["date"].day
    assert d["is_weekend"] == (d["date"].dayofweek >= 5)


# ---------- Fact table ----------

def test_excluded_statuses_are_not_in_fact(result, data):
    _, fact = result
    excluded = data["orders"][data["orders"]["status"].isin(["cancelled", "refunded", "failed"])]
    assert not set(excluded["orderId"]) & set(fact["order_id"])


def test_fact_contains_every_item_of_valid_orders(result, data):
    _, fact = result
    valid = data["orders"][~data["orders"]["status"].isin(["cancelled", "refunded", "failed"])]
    expected = data["orderitems"]["orderId"].isin(valid["orderId"]).sum()
    assert len(fact) == expected


def test_revenue_profit_and_margin(result):
    _, fact = result
    assert (fact["revenue"] - fact["quantity"] * fact["unit_price"]).abs().max() < 0.01
    assert (fact["profit"] - (fact["revenue"] - fact["cost_amount"])).abs().max() < 0.01
    sample = fact[fact["revenue"] > 0].iloc[0]
    assert sample["margin_pct"] == pytest.approx(sample["profit"] / sample["revenue"] * 100, abs=0.01)


def test_fact_foreign_keys_exist_in_dimensions(result):
    dims, fact = result
    assert fact["product_id"].isin(dims["dim_product"]["product_id"]).all()
    assert fact["customer_id"].isin(dims["dim_customer"]["customer_id"]).all()
    assert fact["region_id"].isin(dims["dim_region"]["region_id"]).all()
    assert fact["date_id"].isin(dims["dim_date"]["date_id"]).all()


def test_no_negative_or_zero_values(result):
    _, fact = result
    assert (fact["quantity"] > 0).all()
    assert (fact["revenue"] >= 0).all()


# ---------- Config ----------

@pytest.mark.parametrize(
    "uri, expected",
    [
        ("mongodb+srv://user:secret@cluster0.example.net/db", "mongodb+srv://***:***@cluster0.example.net/db"),
        ("postgresql://bi_admin:pw@localhost:5432/dw", "postgresql://***:***@localhost:5432/dw"),
        ("mongodb://localhost:27017/", "mongodb://localhost:27017/"),
    ],
)
def test_mask_uri_hides_credentials(uri, expected):
    assert mask_uri(uri) == expected
