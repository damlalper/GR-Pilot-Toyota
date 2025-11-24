"""Test HTTP endpoints directly"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test suggestions
print("Testing /api/suggestions/5...")
try:
    response = client.get("/api/suggestions/5")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS!")
        print(response.json())
    else:
        print("ERROR:", response.text)
except Exception as e:
    print("EXCEPTION:", str(e))
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")

# Test driver_dna
print("Testing /api/driver_dna/5...")
try:
    response = client.get("/api/driver_dna/5")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS!")
        # print(response.json())
    else:
        print("ERROR:", response.text)
except Exception as e:
    print("EXCEPTION:", str(e))
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")

# Test pit_strategy
print("Testing /api/pit_strategy/5...")
try:
    response = client.get("/api/pit_strategy/5")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS!")
        # print(response.json())
    else:
        print("ERROR:", response.text)
except Exception as e:
    print("EXCEPTION:", str(e))
    import traceback
    traceback.print_exc()
