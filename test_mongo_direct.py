"""Direct MongoDB test"""
from pymongo import MongoClient

# Direct connection
mongo_uri = "mongodb+srv://rachdioussama33_db_user:nynEYT1HClP8yCc8@cluster0.lu3hrso.mongodb.net/ecom_bi?retryWrites=true&w=majority&appName=Cluster0"
mongo_db = "ecom_bi"

print(f"Connecting to MongoDB...")
print(f"Database: {mongo_db}")

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
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
    print("\n✓ Connection test successful!")
    
except Exception as e:
    print(f"\n✗ Connection failed: {e}")
