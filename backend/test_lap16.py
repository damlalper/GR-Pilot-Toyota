from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("Testing lap 16 suggestions...")
response = client.get("/api/suggestions/16")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

print("\nTesting lap 16 driver_dna...")
response = client.get("/api/driver_dna/16")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

print("\nTesting lap 16 pit_strategy...")
response = client.get("/api/pit_strategy/16")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")
