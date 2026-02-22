#!/usr/bin/env python
"""
Complete Project Test Suite
Tests all frontend-backend connections and features
"""

import requests
import json
import time

API_BASE_URL = 'http://localhost:5000/api'

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print(f"{text:.^70}")
    print(f"{'='*70}{Colors.END}\n")

def print_pass(text):
    print(f"{Colors.GREEN}[PASS]{Colors.END} {text}")

def print_fail(text):
    print(f"{Colors.RED}[FAIL]{Colors.END} {text}")

def print_test(text):
    print(f"{Colors.CYAN}[TEST]{Colors.END} {text}")

def run_tests():
    # Test counters
    tests_passed = 0
    tests_failed = 0
    
    # Store credentials for subsequent tests
    test_email = f'testuser{int(time.time())}@test.com'
    test_password = 'TestPass123!'
    user_token = None
    user_id = None
    
    print_header("AI HEALTH ASSISTANT - FULL SYSTEM TEST")
    
    # ==================== AUTH TESTS ====================
    print_header("1. AUTHENTICATION TESTS")
    
    # Test 1.1: Signup
    print_test("User Signup with all fields")
    try:
        payload = {
            'email': test_email,
            'name': 'Test User',
            'phone': '+1-555-0123',
            'password': test_password,
            'date_of_birth': '1995-01-15',
            'gender': 'male'
        }
        r = requests.post(f'{API_BASE_URL}/auth/signup', json=payload, timeout=5)
        if r.status_code == 201:
            data = r.json()
            user_token = data.get('access_token')
            user_id = data.get('user', {}).get('id')
            print_pass(f"User created - ID: {user_id}, Token: {user_token[:20]}...")
            tests_passed += 1
        else:
            print_fail(f"Status {r.status_code}: {r.json()}")
            tests_failed += 1
    except Exception as e:
        print_fail(f"Error: {e}")
        tests_failed += 1
    
    # Test 1.2: Login
    print_test("User Login with correct credentials")
    try:
        payload = {'email': test_email, 'password': test_password}
        r = requests.post(f'{API_BASE_URL}/auth/login', json=payload, timeout=5)
        if r.status_code == 200:
            data = r.json()
            user_token = data.get('access_token')
            print_pass(f"Login successful - Token received")
            tests_passed += 1
        else:
            print_fail(f"Status {r.status_code}")
            tests_failed += 1
    except Exception as e:
        print_fail(f"Error: {e}")
        tests_failed += 1
    
    # Test 1.3: Wrong password
    print_test("Login rejection with wrong password")
    try:
        payload = {'email': test_email, 'password': 'WrongPass'}
        r = requests.post(f'{API_BASE_URL}/auth/login', json=payload, timeout=5)
        if r.status_code == 401:
            print_pass("Wrong password correctly rejected")
            tests_passed += 1
        else:
            print_fail(f"Should return 401, got {r.status_code}")
            tests_failed += 1
    except Exception as e:
        print_fail(f"Error: {e}")
        tests_failed += 1
    
    # ==================== HEALTH TRACKING TESTS ====================
    print_header("2. HEALTH TRACKING TESTS")
    
    if not user_token:
        print_fail("Skipping health tests - No valid token")
        tests_failed += 3
    else:
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Test 2.1: Update health metrics
        print_test("Update health metrics (heart rate, BP, weight, temperature)")
        try:
            payload = {
                'heart_rate': 72,
                'blood_pressure': '120/80',
                'weight': 75.5,
                'temperature': 37.2
            }
            r = requests.post(f'{API_BASE_URL}/health/update', json=payload, headers=headers, timeout=5)
            if r.status_code == 201:
                print_pass("Health metrics updated successfully")
                tests_passed += 1
            else:
                print_fail(f"Status {r.status_code}: {r.json()}")
                tests_failed += 1
        except Exception as e:
            print_fail(f"Error: {e}")
            tests_failed += 1
        
        # Test 2.2: Retrieve health data
        print_test("Retrieve health history")
        try:
            r = requests.get(f'{API_BASE_URL}/health/data', headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                print_pass(f"Retrieved health data - {len(data.get('records', []))} records")
                tests_passed += 1
            else:
                print_fail(f"Status {r.status_code}")
                tests_failed += 1
        except Exception as e:
            print_fail(f"Error: {e}")
            tests_failed += 1
        
        # Test 2.3: Get health summary
        print_test("Get latest health summary")
        try:
            r = requests.get(f'{API_BASE_URL}/health/summary', headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                hr = data.get('latest_record', {}).get('heart_rate', 'N/A')
                print_pass(f"Summary retrieved - Heart Rate: {hr} bpm")
                tests_passed += 1
            else:
                print_fail(f"Status {r.status_code}")
                tests_failed += 1
        except Exception as e:
            print_fail(f"Error: {e}")
            tests_failed += 1
    
    # ==================== APPOINTMENT TESTS ====================
    print_header("3. APPOINTMENT BOOKING TESTS")
    
    if not user_token:
        print_fail("Skipping appointment tests - No valid token")
        tests_failed += 3
    else:
        headers = {'Authorization': f'Bearer {user_token}'}
        appointment_id = None
        
        # Test 3.1: Book appointment
        print_test("Book doctor appointment")
        try:
            payload = {
                'doctor_name': 'Dr. Smith',
                'specialization': 'General Practice',
                'appointment_date': '2026-02-25',
                'appointment_time': '10:00',
                'reason': 'Regular checkup'
            }
            r = requests.post(f'{API_BASE_URL}/appointments/book', json=payload, headers=headers, timeout=5)
            if r.status_code == 201:
                data = r.json()
                appointment_id = data.get('appointment', {}).get('id')
                print_pass(f"Appointment booked - ID: {appointment_id}")
                tests_passed += 1
            else:
                print_fail(f"Status {r.status_code}: {r.json()}")
                tests_failed += 1
        except Exception as e:
            print_fail(f"Error: {e}")
            tests_failed += 1
        
        # Test 3.2: List appointments
        print_test("Retrieve all appointments")
        try:
            r = requests.get(f'{API_BASE_URL}/appointments/list', headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                count = len(data.get('appointments', []))
                print_pass(f"Appointments retrieved - Total: {count}")
                tests_passed += 1
            else:
                print_fail(f"Status {r.status_code}")
                tests_failed += 1
        except Exception as e:
            print_fail(f"Error: {e}")
            tests_failed += 1
        
        # Test 3.3: Cancel appointment
        if appointment_id:
            print_test("Cancel appointment")
            try:
                r = requests.delete(f'{API_BASE_URL}/appointments/{appointment_id}/cancel', headers=headers, timeout=5)
                if r.status_code == 200:
                    print_pass("Appointment cancelled successfully")
                    tests_passed += 1
                else:
                    print_fail(f"Status {r.status_code}")
                    tests_failed += 1
            except Exception as e:
                print_fail(f"Error: {e}")
                tests_failed += 1
        else:
            tests_failed += 1
    
    # ==================== DIET & EXERCISE TESTS ====================
    print_header("4. DIET & EXERCISE RECOMMENDATIONS")
    
    # Test 4.1: Diet recommendations
    print_test("Get diet recommendations")
    try:
        payload = {'age': 30, 'gender': 'male', 'health_condition': 'normal'}
        r = requests.post(f'{API_BASE_URL}/diet/recommendations', json=payload, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print_pass(f"Diet plan retrieved - Contains {len(str(data))} characters")
            tests_passed += 1
        else:
            print_fail(f"Status {r.status_code}")
            tests_failed += 1
    except Exception as e:
        print_fail(f"Error: {e}")
        tests_failed += 1
    
    # Test 4.2: Exercise recommendations
    print_test("Get exercise recommendations")
    try:
        payload = {'fitness_level': 'intermediate'}
        r = requests.post(f'{API_BASE_URL}/exercise/recommendations', json=payload, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print_pass(f"Exercise plan retrieved - Contains {len(str(data))} characters")
            tests_passed += 1
        else:
            print_fail(f"Status {r.status_code}")
            tests_failed += 1
    except Exception as e:
        print_fail(f"Error: {e}")
        tests_failed += 1
    
    # ==================== CHATBOT TESTS ====================
    print_header("5. CHATBOT TESTS")
    
    chatbot_queries = [
        ('headache', 'remedies'),
        ('fever', 'hydrated'),
        ('diet advice', 'balanced'),
        ('exercise', 'activity'),
        ('stress', 'relax')
    ]
    
    for query, expected_keyword in chatbot_queries:
        print_test(f"Chatbot query: '{query}'")
        try:
            payload = {'message': query}
            r = requests.post(f'{API_BASE_URL}/chatbot/message', json=payload, timeout=5)
            if r.status_code == 200:
                data = r.json()
                response = data.get('response', '')
                if expected_keyword.lower() in response.lower():
                    print_pass(f"Response contains '{expected_keyword}'")
                    tests_passed += 1
                else:
                    print_fail(f"Response doesn't contain '{expected_keyword}'")
                    tests_failed += 1
            else:
                print_fail(f"Status {r.status_code}")
                tests_failed += 1
        except Exception as e:
            print_fail(f"Error: {e}")
            tests_failed += 1
    
    # ==================== SUMMARY ====================
    print_header("TEST SUMMARY")
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"{Colors.GREEN}Tests Passed: {tests_passed}{Colors.END}")
    print(f"{Colors.RED}Tests Failed: {tests_failed}{Colors.END}")
    print(f"{Colors.BOLD}Total Tests: {total_tests}{Colors.END}")
    print(f"{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.END}")
    
    if tests_failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED - PROJECT IS FULLY FUNCTIONAL!{Colors.END}")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Some tests failed - Please review above{Colors.END}")
        return False

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
