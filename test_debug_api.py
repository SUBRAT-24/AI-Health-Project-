#!/usr/bin/env python
"""
Debug API test to see detailed error responses
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5000/api"

print("\n" + "="*70)
print("🐛 DEBUG API TEST")
print("="*70 + "\n")

# Health check
print("1. Testing Health Check...")
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
except Exception as e:
    print(f"   Error: {e}\n")

# Signup
print("2. Testing Signup...")
email = f"testuser{int(time.time())}@example.com"
signup_data = {
    "name": "Test User",
    "email": email,
    "phone": "+1234567890",
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "password": "TestPass123!"
}
try:
    response = requests.post(f"{API_BASE_URL}/auth/signup", json=signup_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    if response.status_code in [200, 201]:
        token = response.json().get('token')
        user_id = response.json().get('user_id')
        print(f"   ✓ Token obtained: {token[:50]}...")
        print(f"   ✓ User ID: {user_id}\n")
    else:
        token = None
        user_id = None
except Exception as e:
    print(f"   Error: {e}\n")
    token = None
    user_id = None

# Test Profile with token
if token:
    print("3. Testing Get Profile with Token...")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   Headers: {headers}")
    try:
        response = requests.get(f"{API_BASE_URL}/auth/profile", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # Test health update
    print("4. Testing Health Update with Token...")
    health_data = {
        "heart_rate": 72,
        "systolic": 120,
        "diastolic": 80,
        "weight": 70.5,
        "temperature": 37.0,
        "blood_glucose": 100,
        "oxygen_saturation": 98,
        "notes": "Test"
    }
    try:
        response = requests.post(f"{API_BASE_URL}/health/update", json=health_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"   Error: {e}\n")

print("="*70)
