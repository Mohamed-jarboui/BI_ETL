"""
Generate a realistic fake e-commerce dataset and load it into MongoDB.

The collections and field names match what the ETL pipeline expects
(users, products, categories, regions, orders, orderitems, payments).
The data is random but reproducible: the same seed always gives the same data.

Usage:
    python scripts/seed_mongo.py                 # uses MONGO_URI / MONGO_DB from .env
    python scripts/seed_mongo.py --seed 7 --orders 5000
"""

import argparse
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

CATEGORIES = {
    "Smartphones": (250, 2800),
    "Laptops": (900, 5500),
    "Audio": (40, 900),
    "Accessories": (10, 150),
    "Home & Kitchen": (25, 1200),
    "Furniture": (120, 2500),
    "Fashion": (20, 350),
    "Shoes": (45, 450),
    "Beauty": (8, 180),
    "Sports": (15, 900),
    "Books": (12, 90),
    "Toys": (10, 300),
    "Groceries": (3, 60),
}

PRODUCT_WORDS = {
    "Smartphones": ["Phone", "Smartphone", "Phone Pro", "Phone Lite"],
    "Laptops": ["Laptop", "Ultrabook", "Notebook", "Gaming Laptop"],
    "Audio": ["Headphones", "Earbuds", "Speaker", "Soundbar"],
    "Accessories": ["Charger", "Phone Case", "USB-C Cable", "Power Bank"],
    "Home & Kitchen": ["Blender", "Coffee Maker", "Air Fryer", "Kettle"],
    "Furniture": ["Desk", "Office Chair", "Bookshelf", "Sofa"],
    "Fashion": ["T-Shirt", "Jacket", "Jeans", "Dress"],
    "Shoes": ["Sneakers", "Running Shoes", "Boots", "Sandals"],
    "Beauty": ["Perfume", "Face Cream", "Shampoo", "Lipstick"],
    "Sports": ["Yoga Mat", "Dumbbells", "Bicycle", "Football"],
    "Books": ["Novel", "Cookbook", "Programming Guide", "Biography"],
    "Toys": ["Puzzle", "Board Game", "Building Blocks", "RC Car"],
    "Groceries": ["Olive Oil", "Coffee Beans", "Dates Box", "Green Tea"],
}

BRANDS = ["Nova", "Atlas", "Orion", "Zenith", "Carthage", "Medina", "Lumen", "Vertex", "Sahara", "Pulse"]

REGIONS = [
    ("Grand Tunis", 0.32),
    ("Sfax", 0.14),
    ("Sousse", 0.12),
    ("Nabeul", 0.10),
    ("Monastir", 0.09),
    ("Bizerte", 0.08),
    ("Gabes", 0.08),
    ("Kairouan", 0.07),
]

ORDER_STATUSES = [
    ("delivered", 0.70),
    ("shipped", 0.08),
    ("processing", 0.04),
    ("pending", 0.03),
    ("cancelled", 0.10),
    ("refunded", 0.05),
]

PAYMENT_METHODS = [("card", 0.45), ("cash_on_delivery", 0.35), ("paypal", 0.12), ("bank_transfer", 0.08)]

START = datetime(2024, 3, 1)
END = datetime(2025, 12, 31)


def _weighted(rng, pairs):
    values, weights = zip(*pairs)
    return rng.choices(values, weights=weights, k=1)[0]


def _order_date(rng):
    """Random date with growth over time and a peak in November-December."""
    span = (END - START).days
    while True:
        day = rng.randint(0, span)
        date = START + timedelta(days=day, minutes=rng.randint(8 * 60, 23 * 60))
        weight = 0.5 + day / span  # sales grow over time
        if date.month in (11, 12):
            weight *= 1.6
        if rng.random() < weight / 2.6:
            return date


def generate_dataset(seed=42, n_users=420, n_products=180, n_orders=2004):
    """Return {collection_name: [documents]} with fake but consistent data."""
    rng = random.Random(seed)
    fake = Faker("fr_FR")
    fake.seed_instance(seed)

    categories = [
        {"categoryId": f"CAT{i:02d}", "categoryName": name}
        for i, name in enumerate(CATEGORIES, start=1)
    ]
    cat_by_name = {c["categoryName"]: c["categoryId"] for c in categories}

    regions = [
        {"regionId": f"REG{i}", "regionName": name, "country": "Tunisia", "continent": "Africa"}
        for i, (name, _) in enumerate(REGIONS, start=1)
    ]
    region_weights = [(r["regionId"], w) for r, (_, w) in zip(regions, REGIONS)]

    products = []
    for i in range(1, n_products + 1):
        category = rng.choice(list(CATEGORIES))
        low, high = CATEGORIES[category]
        price = round(rng.uniform(low, high), 2)
        brand = rng.choice(BRANDS)
        created = START - timedelta(days=rng.randint(0, 120))
        products.append({
            "productId": f"P{i:04d}",
            "productName": f"{brand} {rng.choice(PRODUCT_WORDS[category])} {rng.randint(1, 9)}",
            "categoryId": cat_by_name[category],
            "brand": brand,
            "unitPrice": price,
            "unitCost": round(price * rng.uniform(0.62, 0.85), 2),
            "description": fake.sentence(nb_words=10),
            "createdAt": created,
            "updatedAt": created,
        })
    # Some products sell more than others
    popularity = [rng.lognormvariate(0, 0.7) for _ in products]

    users = []
    for i in range(1, n_users + 1):
        first, last = fake.first_name(), fake.last_name()
        registered = START - timedelta(days=60) + timedelta(days=rng.randint(0, (END - START).days))
        users.append({
            "userId": f"U{i:04d}",
            "firstName": first,
            "lastName": last,
            "email": f"{first}.{last}{i}@example.com".lower().replace(" ", ""),
            "gender": rng.choice(["Male", "Female"]),
            "regionId": _weighted(rng, region_weights),
            "role": "customer",
            "registrationDate": registered,
            "createdAt": registered,
            "updatedAt": registered,
        })
    # Some customers order more often than others
    activity = [rng.lognormvariate(0, 0.6) for _ in users]

    orders, items, payments = [], [], []
    item_id = 1
    for i in range(1, n_orders + 1):
        order_id = f"O{i:05d}"
        user = rng.choices(users, weights=activity, k=1)[0]
        date = _order_date(rng)
        status = _weighted(rng, ORDER_STATUSES)
        n_items = rng.choices([1, 2, 3, 4, 5, 6], weights=[14, 22, 24, 20, 12, 8], k=1)[0]

        total = 0.0
        for product in rng.choices(products, weights=popularity, k=n_items):
            quantity = rng.choices([1, 2, 3, 4], weights=[70, 20, 7, 3], k=1)[0]
            discount = rng.choice([0, 0, 0, 0.05, 0.10, 0.15])
            unit_price = round(product["unitPrice"] * (1 - discount), 2)
            total += unit_price * quantity
            items.append({
                "orderItemId": f"OI{item_id:06d}",
                "orderId": order_id,
                "productId": product["productId"],
                "quantity": quantity,
                "unitPrice": unit_price,
            })
            item_id += 1

        orders.append({
            "orderId": order_id,
            "userId": user["userId"],
            "orderDate": date,
            "status": status,
            "totalAmount": round(total, 2),
            "createdAt": date,
        })

        # Pending and some cancelled orders were never paid
        if status == "pending" or (status == "cancelled" and rng.random() < 0.6):
            continue
        payment_status = {"refunded": "refunded"}.get(status, "completed")
        if payment_status == "completed" and rng.random() < 0.02:
            payment_status = "failed"
        payments.append({
            "paymentId": f"PAY{i:05d}",
            "orderId": order_id,
            "amount": round(total, 2),
            "method": _weighted(rng, PAYMENT_METHODS),
            "status": payment_status,
            "paymentDate": date + timedelta(hours=rng.randint(0, 48)),
        })

    return {
        "categories": categories,
        "regions": regions,
        "products": products,
        "users": users,
        "orders": orders,
        "orderitems": items,
        "payments": payments,
    }


def main():
    from dotenv import load_dotenv
    from pymongo import MongoClient

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    parser = argparse.ArgumentParser(description="Load fake e-commerce data into MongoDB")
    parser.add_argument("--uri", default=os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    parser.add_argument("--db", default=os.getenv("MONGO_DB", "ecommerce"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--users", type=int, default=420)
    parser.add_argument("--products", type=int, default=180)
    parser.add_argument("--orders", type=int, default=2004)
    args = parser.parse_args()

    data = generate_dataset(args.seed, args.users, args.products, args.orders)

    client = MongoClient(args.uri)
    db = client[args.db]
    for name, docs in data.items():
        db[name].drop()
        db[name].insert_many(docs)
        print(f"{name:<11} {len(docs):>6} documents")
    client.close()
    print(f"\nLoaded into database '{args.db}'")


if __name__ == "__main__":
    main()
