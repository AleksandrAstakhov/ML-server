import requests
import time
from data import URL, data

models = [
    {"name": "rf_long", "kind": "rf", "params": {"n_estimators": 100}},
    {"name": "svc_long", "kind": "svc", "params": {"kernel": "rbf", "C": 1.0}},
]

start = time.time()
for model in models:
    print(f"Training {model['name']} synchronously...")
    r = requests.post(f"{URL}/fit", json={**model, **data})
    print(r.status_code, r.text)

print("Sequential training finished in:", time.time() - start, "seconds")
