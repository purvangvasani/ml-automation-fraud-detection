# # main.py

# from fastapi import FastAPI
# from pydantic import BaseModel
# import joblib
# import pandas as pd
# from db import log_transaction, get_recent_transactions

# app = FastAPI()
# model = joblib.load("fraud_model.pkl")

# class Transaction(BaseModel):
#     points_redeemed: float
#     time_of_day: int
#     location_id: int

# @app.post("/predict")
# def detect_fraud(tx: Transaction):
#     df = pd.DataFrame([tx.dict()])
#     result = model.predict(df)
#     score = model.decision_function(df).tolist()[0]

#     res = {
#         "is_fraud": bool(result[0] == -1),  # Convert numpy.bool_ to Python bool
#         "anomaly_score": float(score)       # Convert numpy.float64 to float
#     }

#     log_transaction(tx.dict(), res)
#     return res  # ✅ now fully JSON-serializable

# @app.get("/transactions")
# def recent_logs():
#     return get_recent_transactions()

# @app.get("/health")
# def health():
#     return {"status": "running"}



# main.py

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from db import log_transaction, get_recent_transactions

app = FastAPI()

model = joblib.load("fraud_model.pkl")
required_features = ["tip", "total_amount", "coupon_discount"]

class Transaction(BaseModel):
    tip: float
    total_amount: int
    coupon_discount: float

@app.post("/predict")
def detect_fraud(tx: Transaction):
    df = pd.DataFrame([tx.dict()])

    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]

    result = {
        "is_fraud": bool(prediction),
        "fraud_probability": float(probability)
    }

    # Don't expect 'anomaly_score' anymore
    log_transaction(tx.dict(), result)
    return result

@app.get("/transactions")
def recent_logs():
    return get_recent_transactions()

@app.get("/health")
def health():
    return {"status": "running"}
