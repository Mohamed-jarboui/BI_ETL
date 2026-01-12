"""Check order schema"""
from pymongo import MongoClient
import pandas as pd

mongo_uri = "mongodb+srv://rachdioussama33_db_user:nynEYT1HClP8yCc8@cluster0.lu3hrso.mongodb.net/ecom_bi?retryWrites=true&w=majority&appName=Cluster0"
mongo_db = "ecom_bi"

client = MongoClient(mongo_uri)
db = client[mongo_db]

# Check orders schema
orders = db['orders'].find_one()
print("Orders schema:")
print(list(orders.keys()) if orders else "No orders found")

# Check orderitems schema
order_items = db['orderitems'].find_one()
print("\nOrder Items schema:")
print(list(order_items.keys()) if order_items else "No order items found")

# Check users schema
users = db['users'].find_one()
print("\nUsers schema:")
print(list(users.keys()) if users else "No users found")

# Convert to DataFrame to see columns
print("\n=== SAMPLE DATA ===")
orders_df = pd.DataFrame(list(db['orders'].find().limit(2)))
print("\n Orders columns:", orders_df.columns.tolist())

orderitems_df = pd.DataFrame(list(db['orderitems'].find().limit(2)))
print("\nOrder Items columns:", orderitems_df.columns.tolist())

users_df = pd.DataFrame(list(db['users'].find().limit(2)))
print("\nUsers columns:", users_df.columns.tolist())

client.close()
