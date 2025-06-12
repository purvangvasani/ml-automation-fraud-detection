# db.py

from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "<<MONGO DB URL>>") # Replace with your MongoDB URI
client = MongoClient(MONGO_URI)
db = client["restaurant"]
transactions_collection = db["frauddtransactions"]

def log_transaction(data: dict, result: dict):
    entry = {**data, **result}  # Merge all values (safe if keys don't conflict)
    transactions_collection.insert_one(entry)


def get_recent_transactions(limit=10):
    results = transactions_collection.find().sort("_id", -1).limit(limit)
    return [
        {**doc, "_id": str(doc["_id"])}  # Convert ObjectId to string
        for doc in results
    ]