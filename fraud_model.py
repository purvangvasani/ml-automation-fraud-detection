# # fraud_model.py

# import pandas as pd
# from pymongo import MongoClient
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report
# import joblib

# def fetch_data_from_mongo():
#     MONGO_URI = ""
#     client = MongoClient(MONGO_URI)
#     db = client["restaurant"]
#     collection = db["orders"]

#     pipeline = [
#         {
#             "$lookup": {
#                 "from": "users",
#                 "localField": "user_id",
#                 "foreignField": "_id",
#                 "as": "user_info"
#             }
#         },
#         {
#             "$lookup": {
#                 "from": "staffs",
#                 "localField": "staff_id",
#                 "foreignField": "_id",
#                 "as": "staff_info"
#             }
#         },
#         {
#             "$lookup": {
#                 "from": "coupons",
#                 "localField": "coupon_id",
#                 "foreignField": "_id",
#                 "as": "coupon_info"
#             }
#         },
#         {
#             "$project": {
#                 "_id": 0,
#                 "order_id": 1,
#                 "total_amount": 1,
#                 "tip": 1,
#                 "payment_method": 1,
#                 "user_info.name": 1,
#                 "user_info.email": 1,
#                 "staff_info.name": 1,
#                 "staff_info.role": 1,
#                 "coupon_info.code": 1,
#                 "coupon_info.discount": 1
#             }
#         }
#     ]

#     result = list(collection.aggregate(pipeline))

#     if not result:
#         return pd.DataFrame()
    
#     # Flatten nested arrays like user_info.0.name → user_name
#     df = pd.json_normalize(result)
#     return df.dropna(subset=["total_amount", "tip"])
#     # # Pull features only, exclude MongoDB _id
#     # cursor = collection.find({}, {
#     #     "_id": 0,
#     #     "coupon_id": 1,
#     #     "user_id": 1,
#     #     "staff_id": 1,
#     #     "total_amount": 1,
#     #     "payment_method": 1,
#     #     "tip": 1
#     # })

#     # data = pd.DataFrame(list(cursor))
#     # return data.dropna()

# def label_fraud(data: pd.DataFrame) -> pd.DataFrame:
#     # Drop rows with missing data
#     data = data.dropna(subset=["total_amount", "tip", "coupon_discount"])

#     # Calculate derived features
#     data["tip_percent"] = data["tip"] / data["total_amount"]

#     # Rule-based labeling
#     data["is_fraud"] = (
#         (data["tip_percent"] > 0.25) | 
#         (data["coupon_discount"] > 40)
#     ).astype(int)

#     return data

# def train_model_new():
#     data = fetch_data_from_mongo()

#     if data.empty:
#         print("❌ No data found in MongoDB.")
#         return

#     data = label_fraud(data)

#     feature_cols = ["points_redeemed", "time_of_day", "location_id", "tip", "coupon_discount"]
#     target_col = "is_fraud"

#     if data[target_col].sum() == 0:
#         print("⚠️ No fraudulent samples found. Check your labeling logic or data.")
#         return

#     X = data[feature_cols]
#     y = data[target_col]

#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#     model = RandomForestClassifier(n_estimators=100, random_state=42)
#     model.fit(X_train, y_train)

#     y_pred = model.predict(X_test)
#     print("✅ Model performance:\n", classification_report(y_test, y_pred))

#     joblib.dump(model, "fraud_model.pkl")
#     print("✅ Model trained and saved as fraud_model.pkl")

# # def train_model():
# #     data = pd.DataFrame({
# #         'points_redeemed': [10, 20, 15, 22, 18, 3000, 2500],  # last 2 are frauds
# #         'time_of_day': [10, 12, 13, 9, 11, 3, 4],
# #         'location_id': [1, 1, 2, 2, 1, 5, 6],
# #     })

# #     model = IsolationForest(contamination=0.2, random_state=42)
# #     model.fit(data)

# #     joblib.dump(model, "fraud_model.pkl")
# #     print("Model trained and saved as fraud_model.pkl")

# if __name__ == "__main__":
#     train_model_new()


import pandas as pd
from pymongo import MongoClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

MONGO_URI = "<<MONGO DB URL>>" # Replace with your MongoDB URI
client = MongoClient(MONGO_URI)

def fetch_data_from_mongo(chunk_size=1000):
    db = client["restaurant"]
    collection = db["orders"]

    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "user_info"
            }
        },
        {
            "$lookup": {
                "from": "staffs",
                "localField": "staff_id",
                "foreignField": "staff_id",
                "as": "staff_info"
            }
        },
        {
            "$lookup": {
                "from": "coupons",
                "localField": "coupon_id",
                "foreignField": "coupon_id",
                "as": "coupon_info"
            }
        },
        {
            "$project": {
                "_id": 0,
                "order_id": 1,
                "total_amount": 1,
                "tip": 1,
                "payment_method": 1,
                "user_info.name": 1,
                "user_info.email": 1,
                "staff_info.name": 1,
                "staff_info.role": 1,
                "coupon_info.code": 1,
                "coupon_info.discount_percent": 1
            }
        }
    ]

    cursor = collection.aggregate(pipeline, allowDiskUse=True)
    buffer = []

    for doc in cursor:
        buffer.append(doc)
        if len(buffer) >= chunk_size:
            # Yield (processed_df, raw_docs) for prediction or update loop
            yield preprocess_chunk(buffer), buffer
            buffer = []

    if buffer:
        # Yield (processed_df, raw_docs) for prediction or update loop
        yield preprocess_chunk(buffer), buffer

def preprocess_chunk(raw_docs):
    df = pd.json_normalize(raw_docs)

    # Extract discount_percent from first coupon (if any)
    def extract_discount(row):
        if isinstance(row, list) and len(row) > 0:
            return row[0].get("discount_percent", 0)
        return 0

    df["coupon_discount"] = df["coupon_info"].apply(extract_discount)
    
    # Rename joined fields for easier access
    df = df.rename(columns={
        "user_info.0.name": "user_name",
        "staff_info.0.name": "staff_name",
        "staff_info.0.role": "staff_role"
    })

    # Ensure other fields exist
    for col in ["tip", "total_amount", "coupon_discount"]:
        if col not in df.columns:
            df[col] = 0

    return df.dropna(subset=["total_amount", "tip", "coupon_discount"])


def label_fraud(data: pd.DataFrame) -> pd.DataFrame:
    # Rule-based label
    data["is_fraud"] = (
        (data["tip"] > 0.25 * data["total_amount"]) |
        (data["coupon_discount"] > 40)
    ).astype(int)

    return data

def train_model_new():
    print("🚀 Starting model training from MongoDB in chunks...")

    full_data = []
    for chunk_df, _ in fetch_data_from_mongo(chunk_size=10):
        if chunk_df.empty:
            continue

        chunk_df = label_fraud(chunk_df)
        full_data.append(chunk_df)

    if not full_data:
        print("❌ No valid data found.")
        return

    data = pd.concat(full_data, ignore_index=True)

    if data["is_fraud"].sum() == 0:
        print("⚠️ No fraud samples found in the data. Adjust your rules or check data quality.")
        return

    feature_cols = ["tip", "total_amount", "coupon_discount"]
    target_col = "is_fraud"

    X = data[feature_cols]
    y = data[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("✅ Model performance:\n", classification_report(y_test, y_pred, zero_division=1))

    joblib.dump(model, "fraud_model.pkl")
    print("✅ Model trained and saved as fraud_model.pkl")


if __name__ == "__main__":
    train_model_new()
