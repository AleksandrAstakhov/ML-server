import requests
from data import URL

model_names = ["rf_long", "svc_long", "rf_async", "svc_async"]

for name in model_names:
    print(f"Unloading {name}...")
    r = requests.post(f"{URL}/unload", json={"name": name})
    print(r.status_code, r.text)

for name in model_names:
    print(f"Removing {name}...")
    r = requests.delete(f"{URL}/remove", json={"name": name})
    print(r.status_code, r.text)

print("Removing all remaining models...")
r = requests.delete(f"{URL}/remove_all")
print(r.status_code, r.text)
