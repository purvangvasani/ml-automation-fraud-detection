# ml-automation-fraud-detection

## Install relevant packages from requirement.txt
```bash
pip install -r requirements
```

### To write requirement.txt file with updated packages
```bash
pip freeze > requirements. txt
```

## Initiate new virtual environment
```bash
python3 -m venv my_project_env
```

### Start virtual environment
```bash
source <my_project_env>/bin/activate
```

## Update Mongo DB URL
Search and replace <<MONGO DB URL>> with your DB-URL


## To Train Model
```bash
python fraud_model.py 
```

## To Run Trained Model
```bash
uvicorn main:app --reload
```

## To test with data
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"tip": 10, "total_amount": 100,  "coupon_discount": 20}'
```

## To check logs
```bash
curl http://127.0.0.1:8000/transactions
```
