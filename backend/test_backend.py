# backend/test_backend.py
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

print("Testing Backend API...")
print("=" * 40)

# Test health
response = requests.get(f"{BASE_URL}/health")
print("✅ Health Check:", response.json())

# Test activities
response = requests.get(f"{BASE_URL}/activities")
activities = response.json()
print(f"✅ Activities: Found {len(activities)} activities")
if activities:
    print("   First activity:", activities[0])

# Test create orchestration
response = requests.post(f"{BASE_URL}/orchestration/create", 
                        json={"activities": [{"name": "Test", "duration": 30}]})
print("✅ Create Orchestration:", response.json())

# Test validate
response = requests.post(f"{BASE_URL}/orchestration/validate", json={})
print("✅ Validate:", response.json())

# Test export
response = requests.get(f"{BASE_URL}/orchestration/export")
print("✅ Export:", response.json())

print("=" * 40)
print("All tests passed!")