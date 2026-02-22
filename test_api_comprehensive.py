#!/usr/bin/env python
"""
Comprehensive API Test Script
Tests all endpoints and verifies frontend can connect
"""

import requests
import json
import time
import sys

API_BASE_URL = "http://localhost:5000/api"

# Test results tracker
test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def print_test(name, passed, message=""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  [{status}] {name}")
    if message:
        print(f"       {message}")
    if passed:
        test_results['passed'] += 1
    else:
        test_results['failed'] += 1

print("\n" + "="*70)
print("🧪 AI HEALTH ASSISTANT - COMPREHENSIVE API TEST SUITE")
print("="*70 + "\n")

# ========================
# HEALTH CHECK
# ========================
print("📊 HEALTH CHECK:")
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    print_test("API Health Check", response.status_code == 200, f"Status: {response.status_code}")
except Exception as e:
    print_test("API Health Check", False, f"Error: {str(e)}")
    print("\n❌ Backend is not running! Please start backend_no_orm.py first.")
    sys.exit(1)

# ========================
# AUTHENTICATION
# ========================
print("\n🔐 AUTHENTICATION TESTS:")

# Test signup
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
    passed = response.status_code in [200, 201]
    print_test("Signup", passed, f"Status: {response.status_code}")
    
    if passed:
        signup_response = response.json()
        token = signup_response.get('token')
        user_id = signup_response.get('user_id')
    else:
        print(f"       Response: {response.json()}")
except Exception as e:
    print_test("Signup", False, f"Error: {str(e)}")
    token = None
    user_id = None

# Test login
try:
    login_data = {
        "email": email,
        "password": "TestPass123!"
    }
    response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
    passed = response.status_code == 200
    print_test("Login", passed, f"Status: {response.status_code}")
    
    if passed and response.status_code == 200:
        login_response = response.json()
        token = login_response.get('token')
        user_id = login_response.get('user_id')
except Exception as e:
    print_test("Login", False, f"Error: {str(e)}")

# Test get profile
if token:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/auth/profile", headers=headers)
        passed = response.status_code == 200
        print_test("Get Profile", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Get Profile", False, f"Error: {str(e)}")

# ========================
# HEALTH RECORDS
# ========================
print("\n❤️ HEALTH RECORDS TESTS:")

if token:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        health_data = {
            "heart_rate": 72,
            "systolic": 120,
            "diastolic": 80,
            "weight": 70.5,
            "temperature": 37.0,
            "blood_glucose": 100,
            "oxygen_saturation": 98,
            "notes": "Regular checkup"
        }
        response = requests.post(f"{API_BASE_URL}/health/update", json=health_data, headers=headers)
        passed = response.status_code in [200, 201]
        print_test("Update Health Metrics", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Update Health Metrics", False, f"Error: {str(e)}")
    
    # Get health data
    try:
        response = requests.get(f"{API_BASE_URL}/health/data", headers=headers)
        passed = response.status_code == 200
        print_test("Get Health Data", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Get Health Data", False, f"Error: {str(e)}")
    
    # Get health summary
    try:
        response = requests.get(f"{API_BASE_URL}/health/summary", headers=headers)
        passed = response.status_code == 200
        print_test("Get Health Summary", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Get Health Summary", False, f"Error: {str(e)}")
else:
    print("  [⊘ SKIP] Skipping protected endpoints (no token)")

# ========================
# APPOINTMENTS
# ========================
print("\n📅 APPOINTMENTS TESTS:")

if token:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        appointment_data = {
            "doctor_name": "Dr. John Smith",
            "specialization": "General Medicine",
            "appointment_date": "2026-02-20T10:00:00",
            "reason": "Regular checkup"
        }
        response = requests.post(f"{API_BASE_URL}/appointments/book", json=appointment_data, headers=headers)
        passed = response.status_code in [200, 201]
        print_test("Book Appointment", passed, f"Status: {response.status_code}")
        
        if passed:
            appointment_id = response.json().get('id')
        else:
            appointment_id = None
    except Exception as e:
        print_test("Book Appointment", False, f"Error: {str(e)}")
        appointment_id = None
    
    # Get appointments
    try:
        response = requests.get(f"{API_BASE_URL}/appointments/list", headers=headers)
        passed = response.status_code == 200
        print_test("Get Appointments", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Get Appointments", False, f"Error: {str(e)}")
    
    # Update appointment
    if appointment_id:
        try:
            update_data = {"status": "confirmed", "notes": "Confirmed by doctor"}
            response = requests.put(f"{API_BASE_URL}/appointments/{appointment_id}/update", json=update_data, headers=headers)
            passed = response.status_code == 200
            print_test("Update Appointment", passed, f"Status: {response.status_code}")
        except Exception as e:
            print_test("Update Appointment", False, f"Error: {str(e)}")
else:
    print("  [⊘ SKIP] Skipping protected endpoints (no token)")

# ========================
# CHATBOT
# ========================
print("\n🤖 CHATBOT TESTS:")

try:
    response = requests.get(f"{API_BASE_URL}/chatbot/health-tips")
    passed = response.status_code == 200
    print_test("Get Health Tips", passed, f"Status: {response.status_code}")
except Exception as e:
    print_test("Get Health Tips", False, f"Error: {str(e)}")

try:
    message_data = {"message": "How do I stay healthy?"}
    response = requests.post(f"{API_BASE_URL}/chatbot/message", json=message_data)
    passed = response.status_code == 200
    print_test("Chatbot Message", passed, f"Status: {response.status_code}")
except Exception as e:
    print_test("Chatbot Message", False, f"Error: {str(e)}")

# ========================
# SUMMARY
# ========================
print("\n" + "="*70)
print(f"📈 TEST SUMMARY")
print("="*70)
print(f"✓ Passed:  {test_results['passed']}")
print(f"✗ Failed:  {test_results['failed']}")
print(f"📊 Total:  {test_results['passed'] + test_results['failed']}")
print("="*70 + "\n")

if test_results['failed'] == 0:
    print("✅ ALL TESTS PASSED! Backend is working correctly.")
else:
    print(f"⚠️  {test_results['failed']} test(s) failed. Check the errors above.")

print("\n")
