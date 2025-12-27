import requests
import time
import random

url = "http://127.0.0.1:8000/ingest"

services = ["auth-service", "payment-gateway", "frontend-ui", "db-shard-01"]
levels = ["INFO", "WARN", "ERROR", "CRITICAL"]

print("🚀 Starting Stress Test: Sending 1000 logs...")
start_time = time.time()

for i in range(1000):
    payload = {
        "service": random.choice(services),
        "level": random.choice(levels),
        "message": f"Stress test log entry {i} - checking system integrity"
    }
    # Send request
    try:
        requests.post(url, json=payload, timeout=0.5)
    except:
        pass

duration = time.time() - start_time
print(f"✅ Finished in {duration:.2f} seconds.")
print(f"⚡ Throughput: {1000 / duration:.0f} logs/second")
