"""Quick test of MongoDB connection and data availability"""
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Connect to MongoDB
mongo_uri = os.getenv('MONGO_URI')
mongo_db = os.getenv('MONGO_DB')

print(f"Connecting to MongoDB...")
print(f"Database: {mongo_db}")

client = MongoClient(mongo_uri)
db = client[mongo_db]

# List collections
print(f"\nAvailable collections:")
collections = db.list_collection_names()
for coll in collections:
    count = db[coll].count_documents({})
    print(f"  - {coll}: {count} documents")

# Check for expected collections
expected = ['users', 'products', 'orders', 'order_items', 'payments', 'regions', 'categories']
print(f"\nExpected collections status:")
for coll in expected:
    if coll in collections:
        count = db[coll].count_documents({})
        print(f"  ✓ {coll}: {count} documents")
    else:
        print(f"  ✗ {coll}: NOT FOUND")

client.close()
print("\nConnection test complete!")
