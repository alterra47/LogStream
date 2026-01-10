import requests
import time
import random
import uuid

# Configuration
INGEST_URL = "http://127.0.0.1:8000/ingest"
SEARCH_URL = "http://127.0.0.1:8000/search"
LOG_COUNT = 1000

# FIX: Removed underscore (_) so C++ keeps it as one token
BATCH_ID = f"TEST{str(uuid.uuid4())[:8]}" 

services = ["auth-service", "payment-gateway", "frontend-ui", "db-shard-01"]
levels = ["INFO", "WARN", "ERROR", "CRITICAL"]

print(f"🚀 Starting Stress Test: Sending {LOG_COUNT} logs...")
print(f"🏷️  Batch ID: {BATCH_ID}")

print("🔥 Warming up connection...")
warmup_id = f"WARM{str(uuid.uuid4())[:8]}"
while True:
    try:
        # Send 1 log
        requests.post(INGEST_URL, json={
            "service": "warmup", 
            "level": "INFO", 
            "message": f"[{warmup_id}] Warmup"
        })
        # Check if C++ sees it
        time.sleep(0.5)
        resp = requests.get(SEARCH_URL, params={"term": warmup_id})
        if resp.json().get("count", 0) > 0:
            print("✅ System is ready! Starting flood...")
            break
        print("... waiting for C++ to connect ...")
    except:
        print("... connecting ...")
    time.sleep(1)

start_time = time.time()

# --- PHASE 1: INGESTION ---
for i in range(LOG_COUNT):
    payload = {
        "service": random.choice(services),
        "level": random.choice(levels),
        # The brackets [] will be stripped by C++ (which is fine), 
        # leaving BATCH_ID as a clean token.
        "message": f"[{BATCH_ID}] Stress test log entry {i} - checking system integrity"
    }
    
    try:
        requests.post(INGEST_URL, json=payload, timeout=0.5)
    except requests.exceptions.RequestException as e:
        # Pass on timeout/connection error (common in stress tests)
        pass

duration = time.time() - start_time
print(f"✅ Ingestion Finished in {duration:.2f} seconds.")
if duration > 0:
    print(f"⚡ Throughput: {LOG_COUNT / duration:.0f} logs/second")

# --- PHASE 2: VERIFICATION ---
print("\n⏳ Waiting 2 seconds for C# SQL Writer & C++ Indexer to catch up...")
time.sleep(2) 

print(f"🔍 Verifying data integrity via Search API...")
try:
    # Now searching for "TESTa1b2c3d4" will match the token in C++
    response = requests.get(SEARCH_URL, params={"term": BATCH_ID})
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.text}")
        exit()

    data = response.json()
    found_count = data.get("count", 0)
    
    print(f"📊 Results:")
    print(f"   - Logs Sent:   {LOG_COUNT}")
    print(f"   - Logs Found:  {found_count}")
    
    if found_count == LOG_COUNT:
        print(f"🎉 SUCCESS: 100% Data Integrity Verified!")
    elif found_count > 0:
        print(f"⚠️  WARNING: Some logs missing. Found {found_count}/{LOG_COUNT}")
    else:
        print(f"❌ FAILURE: No logs found. Tokenization mismatch or C++ Lag.")

except Exception as e:
    print(f"❌ Verification Failed: {e}")