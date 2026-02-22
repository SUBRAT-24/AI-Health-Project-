#!/usr/bin/env python
"""
Backend API Test Script
Tests all major endpoints to verify functionality
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5000/api"

def test_signup():
    """Test user signup endpoint"""
    print("\n[TEST] Testing Signup Endpoint...")
    
    payload = {
        "name": "Test User",
        "email": f"testuser{int(time.time())}@example.com",
        "phone": "+1234567890",
        "date_of_birth": "1990-01-15",
        "gender": "male",
        "password": "TestPass123!"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/signup", json=payload)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("  [OK] Signup test passed")
            return payload['email'], payload['password']
        else:
            print("  [ERROR] Signup test failed")
            return None, None
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return None, None

def test_login(email, password):
    """Test user login endpoint"""
    print("\n[TEST] Testing Login Endpoint...")
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json=payload)
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Response Keys: {list(data.keys())}")
        
        if response.status_code == 200 and 'access_token' in data:
            print("  [OK] Login test passed")
            return data['access_token']
        else:
            print("  [ERROR] Login test failed")
            return None
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return None

def test_health_update(token):
    """Test health update endpoint"""
    print("\n[TEST] Testing Health Update Endpoint...")
    
    if not token:
        print("  [WARN] No token available, skipping")
        return
    
    payload = {
        "heart_rate": 72,
        "blood_pressure": "120/80",
        "weight": 75,
        "temperature": 37.0
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_BASE_URL}/health/update", json=payload, headers=headers)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("  [OK] Health update test passed")
        else:
            print("  [ERROR] Health update test failed")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

def test_appointments_list(token):
    """Test appointments list endpoint"""
    print("\n[TEST] Testing Appointments List Endpoint...")
    
    if not token:
        print("  [WARN] No token available, skipping")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE_URL}/appointments/list", headers=headers)
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Response Type: {type(data)}")
        
        if response.status_code == 200:
            print("  [OK] Appointments list test passed")
        else:
            print("  [ERROR] Appointments list test failed")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

def test_chatbot(message="I have a headache"):
    """Test chatbot endpoint"""
    print("\n[TEST] Testing Chatbot Endpoint...")
    
    payload = {"message": message}
    
    try:
        response = requests.post(f"{API_BASE_URL}/chatbot/message", json=payload)
        print(f"  Status: {response.status_code}")
        data = response.json()
        
        if 'response' in data or 'message' in data:
            response_text = data.get('response', data.get('message', ''))
            print(f"  ChatBot Response: {response_text[:80]}...")
            print("  [OK] Chatbot test passed")
        else:
            print(f"  Response: {data}")
            print("  [WARN] Unexpected response format")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("[LAB] Backend API Testing Suite")
    print("="*60)
    print(f"Testing API at: {API_BASE_URL}\n")
    
    # Wait for server to be ready
    print("[WAIT] Waiting for API server to be ready...")
    for i in range(10):
        try:
            response = requests.get(API_BASE_URL)
            print("[OK] API server is ready!\n")
            break
        except:
            if i < 9:
                time.sleep(1)
            else:
                print("[ERROR] API server not responding\n")
                return
    
    # Run tests
    print("="*60)
    print("Running Tests...")
    print("="*60)
    
    email, password = test_signup()
    token = test_login(email, password) if email else None
    test_health_update(token)
    test_appointments_list(token)
    test_chatbot()
    
    # Summary
    print("\n" + "="*60)
    print("[OK] Testing Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
