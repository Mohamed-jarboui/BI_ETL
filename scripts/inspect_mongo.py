"""
Print the collections, document counts and field names of the source MongoDB.
Useful to check the connection and the schema before running the ETL.

Usage:
    python scripts/inspect_mongo.py          # uses MONGO_URI / MONGO_DB from .env
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

EXPECTED = ["users", "products", "categories", "regions", "orders", "orderitems", "payments"]


def main():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    db = client[os.getenv("MONGO_DB", "ecommerce")]
    existing = set(db.list_collection_names())

    for name in EXPECTED:
        if name not in existing:
            print(f"✗ {name:<11} missing")
            continue
        sample = db[name].find_one() or {}
        fields = ", ".join(k for k in sample if k != "_id")
        print(f"✓ {name:<11} {db[name].count_documents({}):>6} docs | {fields}")

    client.close()


if __name__ == "__main__":
    main()
