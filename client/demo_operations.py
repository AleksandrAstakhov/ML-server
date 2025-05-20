import requests
from common_data import base_url

model_names = ["rf_long", "svc_long", "rf_async", "svc_async"]

for name in model_names:
    print(f"Unloading {name}...")
    r = requests.post(f"{base_url}/unload", json={"name": name})
    print(r.status_code, r.text)

for name in model_names:
    print(f"Removing {name}...")
    r = requests.delete(f"{base_url}/remove", json={"name": name})
    print(r.status_code, r.text)

print("Removing all remaining models...")
r = requests.delete(f"{base_url}/remove_all")
print(r.status_code, r.text)
