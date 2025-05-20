import time
import os

print("Waiting for server to start...")
time.sleep(3)

print("\n Sequential Fit")
os.system("python sync_fit.py")

print("\n Async Fit")
os.system("python async_fit.py")

print("\n Async Predict")
os.system("python async_predict.py")

print("\n Demo Operations")
os.system("python else_operations.py")

print("\nAll tests completed.")
