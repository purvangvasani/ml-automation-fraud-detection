# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import List, Any, Dict
# import joblib
# import pandas as pd
# from datetime import datetime

# app = FastAPI()
# model = joblib.load("fraud_model.pkl")

# class Transaction(BaseModel):
#     tip: float
#     total_amount: float
#     coupon_discount: float
#     is_vpn_used: bool = False
#     country_code: str = "IN"
#     billing_country: str = "IN"

# class Rule(BaseModel):
#     field: str
#     operator: str
#     value: Any
#     label: str

# def evaluate_rule(rule, data):
#     field = rule["field"]
#     operator = rule["operator"]
#     value = rule["value"]
#     left = data.get(field)
#     if isinstance(value, str) and value in data:
#         value = data[value]
#     return {
#         "==": left == value,
#         "!=": left != value,
#         ">": left > value,
#         "<": left < value,
#         ">=": left >= value,
#         "<=": left <= value,
#     }.get(operator, False)

# def apply_dynamic_rules(data: Dict, rules: List[Dict]) -> List[str]:
#     return [r["label"] for r in rules if evaluate_rule(r, data)]

# @app.post("/predict")
# def predict_fraud(tx: Transaction, rules: List[Rule]):
#     features = pd.DataFrame([{
#         "tip": tx.tip,
#         "total_amount": tx.total_amount,
#         "coupon_discount": tx.coupon_discount
#     }])
    
#     model_score = model.predict_proba(features)[0][1]
#     model_fraud = model_score > 0.85

#     tx_data = tx.dict()
#     rules_data = [r.dict() for r in rules]
#     triggered = apply_dynamic_rules(tx_data, rules_data)

#     is_fraud = model_fraud or len(triggered) > 0

#     return {
#         "timestamp": datetime.utcnow().isoformat(),
#         "is_fraud": is_fraud,
#         "model_score": model_score,
#         "rules_triggered": triggered
#     }


# from pymongo import MongoClient
# import pandas as pd
# import joblib
# from fraud_model import fetch_data_from_mongo

# # Load the trained model
# model = joblib.load("fraud_model.pkl")

# # Connect to MongoDB
# client = MongoClient("mongodb+srv://purvangvspark:os1gkUWWK7ILp3K4@cluster0.bmqyx0g.mongodb.net/")
# db = client["restaurant"]
# collection = db["orders"]

# # Fetch all records
# cursor = collection.find({})
# records = list(cursor)

# # Convert to DataFrame
# df = fetch_data_from_mongo()

# # Make sure required fields exist
# required_features = ["tip", "total_amount", "coupon_discount"]
# df = df[required_features]

# # Run predictions
# predictions = model.predict(df)
# probabilities = model.predict_proba(df)[:, 1]

# # Attach results back to each record
# for i, record in enumerate(records):
#     record_id = record["_id"]
#     fraud_flag = bool(predictions[i])
#     fraud_score = float(probabilities[i])
    
#     # Update record in MongoDB
#     collection.update_one(
#         {"_id": record_id},
#         {"$set": {
#             "fraud_flag": fraud_flag,
#             "fraud_score": fraud_score
#         }}
#     )

# print("✅ Predictions added to all documents.")


from pymongo import MongoClient
import pandas as pd
import joblib
from fraud_model import fetch_data_from_mongo  # must yield (df, raw_records)

# Load the trained model
model = joblib.load("fraud_model.pkl")

# Connect to MongoDB
client = MongoClient("<<MONGO DB URL>>")  # Replace with your MongoDB URI
db = client["restaurant"]
collection = db["orders"]

# Process data in chunks
chunk_size = 100  # Adjust for your memory/scale

for df, raw_records in fetch_data_from_mongo(chunk_size=chunk_size):
    required_features = ["tip", "total_amount", "coupon_discount"]
    
    # Skip chunk if required columns missing or empty
    if df.empty or not all(col in df.columns for col in required_features):
        continue
    
    df = df[required_features]

    # Predict fraud and score
    predictions = model.predict(df)
    probabilities = model.predict_proba(df)[:, 1]

    for i, record in enumerate(raw_records):
        record_id = record.get("_id")
        if not record_id:
            continue

        fraud_flag = bool(predictions[i])
        fraud_score = float(probabilities[i])

        # Update MongoDB record
        collection.update_one(
            {"_id": record_id},
            {"$set": {
                "fraud_flag": fraud_flag,
                "fraud_score": fraud_score
            }}
        )

    print(f"✅ Processed and updated {len(df)} records.")

