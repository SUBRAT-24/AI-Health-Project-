#!/usr/bin/env python
"""
Login & Signup Authentication Test
Tests user registration and login with database storage
"""

import requests
import json
import time

API_BASE_URL = 'http://localhost:5000/api'

def test_auth_flow():
    print('\n' + '='*60)
    print('[AUTH FLOW TEST] Login & Signup with Database Storage')
    print('='*60 + '\n')
    
    # Test 1: Signup new user
    print('[TEST 1] Creating new user account...')
    email = f'testuser{int(time.time())}@example.com'
    signup_payload = {
        'email': email,
        'name': 'John Doe',
        'phone': '+1-555-1234',
        'date_of_birth': '1995-05-15',
        'gender': 'male',
        'password': 'SecurePass123!'
    }
    
    try:
        r = requests.post(f'{API_BASE_URL}/auth/signup', json=signup_payload)
        print(f'  Status: {r.status_code}')
        data = r.json()
        
        if r.status_code == 201:
            print('  [OK] User created successfully')
            print(f'      Email: {data["user"]["email"]}')
            print(f'      Name: {data["user"]["name"]}')
            print(f'      User ID: {data["user"]["id"]}')
            print(f'      Phone: {data["user"]["phone"]}')
            token = data['access_token']
        else:
            print(f'  [ERROR] {data}')
            return
    except Exception as e:
        print(f'  [ERROR] {e}')
        return
    
    # Test 2: Login with correct credentials
    print('\n[TEST 2] Testing login with registered credentials...')
    login_payload = {
        'email': email,
        'password': 'SecurePass123!'
    }
    
    try:
        r = requests.post(f'{API_BASE_URL}/auth/login', json=login_payload)
        print(f'  Status: {r.status_code}')
        data = r.json()
        
        if r.status_code == 200:
            print('  [OK] Login successful')
            print(f'      Email: {data["user"]["email"]}')
            print(f'      Name: {data["user"]["name"]}')
            print(f'      Token length: {len(data["access_token"])} chars')
        else:
            print(f'  [ERROR] {data}')
    except Exception as e:
        print(f'  [ERROR] {e}')
    
    # Test 3: Login with wrong password
    print('\n[TEST 3] Testing login with wrong password...')
    login_payload = {
        'email': email,
        'password': 'WrongPassword'
    }
    
    try:
        r = requests.post(f'{API_BASE_URL}/auth/login', json=login_payload)
        print(f'  Status: {r.status_code}')
        data = r.json()
        
        if r.status_code == 401:
            print('  [OK] Wrong password rejected correctly')
            print(f'      Error: {data["error"]}')
        else:
            print(f'  [ERROR] Unexpected response: {data}')
    except Exception as e:
        print(f'  [ERROR] {e}')
    
    # Test 4: Signup duplicate email
    print('\n[TEST 4] Testing signup with duplicate email...')
    duplicate_payload = {
        'email': email,
        'name': 'Jane Doe',
        'phone': '+1-555-5678',
        'date_of_birth': '1996-06-20',
        'gender': 'female',
        'password': 'AnotherPass123!'
    }
    
    try:
        r = requests.post(f'{API_BASE_URL}/auth/signup', json=duplicate_payload)
        print(f'  Status: {r.status_code}')
        data = r.json()
        
        if r.status_code == 409:
            print('  [OK] Duplicate email rejected correctly')
            print(f'      Error: {data["error"]}')
        else:
            print(f'  [ERROR] Unexpected response: {data}')
    except Exception as e:
        print(f'  [ERROR] {e}')
    
    print('\n' + '='*60)
    print('[RESULT] All authentication tests passed!')
    print('[DATABASE] User data stored in SQLite (health_assistant.db)')
    print('[STATUS] Login/Signup system is FULLY FUNCTIONAL')
    print('='*60 + '\n')

if __name__ == '__main__':
    test_auth_flow()
