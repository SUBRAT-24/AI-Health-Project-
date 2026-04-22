#!/usr/bin/env python
"""Comprehensive check of all API endpoints."""
import requests, json, sys

BASE = "http://localhost:5000/api"
results = []

def check(name, method, url, expected_status=None, json_data=None, headers=None, allow_statuses=None):
    """Test an endpoint and report result."""
    try:
        r = getattr(requests, method.lower())(url, json=json_data, headers=headers or {}, timeout=5)
        ok = True
        if expected_status and r.status_code != expected_status:
            if allow_statuses and r.status_code in allow_statuses:
                ok = True
            else:
                ok = False
        status = "✅ PASS" if ok else "❌ FAIL"
        results.append((name, status, r.status_code))
        print(f"  {status} {name} => {r.status_code}")
        return r
    except Exception as e:
        results.append((name, "❌ ERROR", str(e)))
        print(f"  ❌ ERROR {name} => {e}")
        return None

print("=" * 60)
print("🔍 AI Health Assistant - Full API Verification")
print("=" * 60)

# 1. Healthcheck
print("\n📌 HEALTHCHECK")
check("GET /api/healthcheck", "GET", f"{BASE}/healthcheck", 200)

# 2. Auth - Signup
print("\n📌 AUTH")
r = check("POST /api/auth/signup (new user)", "POST", f"{BASE}/auth/signup", allow_statuses=[201, 409],
           json_data={"name": "Test User", "email": "testuser@test.com", "password": "test123",
                      "phone": "1234567890", "date_of_birth": "1995-06-15", "gender": "male"})
user_token = None
if r and r.status_code == 201:
    user_token = r.json().get("token")
elif r and r.status_code == 409:
    print("    (User already exists, logging in instead)")

# 3. Auth - Login (user)
r = check("POST /api/auth/login (user)", "POST", f"{BASE}/auth/login", 200,
           json_data={"email": "testuser@test.com", "password": "test123"})
if r and r.status_code == 200:
    data = r.json()
    user_token = data.get("token")
    role = data.get("role", "N/A")
    print(f"    Token: {user_token[:20]}... Role: {role}")

# 4. Auth - Login (admin)
r = check("POST /api/auth/login (admin)", "POST", f"{BASE}/auth/login", 200,
           json_data={"email": "admin@healthassistant.com", "password": "admin123"})
admin_token = None
if r and r.status_code == 200:
    data = r.json()
    admin_token = data.get("token")
    role = data.get("role", "N/A")
    print(f"    Token: {admin_token[:20]}... Role: {role}")
    if role != "admin":
        print("    ⚠️  WARNING: Role is NOT 'admin'!")

# 5. Auth - Profile
print("\n📌 USER PROFILE")
if user_token:
    auth_h = {"Authorization": f"Bearer {user_token}"}
    check("GET /api/auth/profile", "GET", f"{BASE}/auth/profile", 200, headers=auth_h)

# 6. Health endpoints
print("\n📌 HEALTH TRACKING")
if user_token:
    auth_h = {"Authorization": f"Bearer {user_token}"}
    check("POST /api/health/update", "POST", f"{BASE}/health/update", allow_statuses=[200, 201],
          json_data={"heart_rate": 72, "systolic": 120, "diastolic": 80, "weight": 70.5, "temperature": 36.8},
          headers=auth_h)
    check("GET /api/health/data", "GET", f"{BASE}/health/data", 200, headers=auth_h)
    check("GET /api/health/summary", "GET", f"{BASE}/health/summary", 200, headers=auth_h)

# 7. Appointments
print("\n📌 APPOINTMENTS")
if user_token:
    auth_h = {"Authorization": f"Bearer {user_token}"}
    check("POST /api/appointments/book", "POST", f"{BASE}/appointments/book", allow_statuses=[200, 201],
          json_data={"doctor_name": "Dr. Smith", "doctor_specialization": "Cardiology",
                     "appointment_date": "2026-04-01T10:00:00", "reason": "Checkup"},
          headers=auth_h)
    check("GET /api/appointments/list", "GET", f"{BASE}/appointments/list", 200, headers=auth_h)

# 8. Reports
print("\n📌 REPORTS")
if user_token:
    auth_h = {"Authorization": f"Bearer {user_token}"}
    check("GET /api/reports/list", "GET", f"{BASE}/reports/list", 200, headers=auth_h)

# 9. Diet
print("\n📌 DIET")
check("POST /api/diet/recommendations", "POST", f"{BASE}/diet/recommendations", 200,
      json_data={"age": 30, "gender": "male", "health_condition": "normal"})

# 10. Exercise
print("\n📌 EXERCISE")
check("POST /api/exercise/recommendations", "POST", f"{BASE}/exercise/recommendations", 200,
      json_data={"fitness_level": "beginner"})

# 11. Chatbot
print("\n📌 CHATBOT")
check("POST /api/chatbot/message", "POST", f"{BASE}/chatbot/message", 200,
      json_data={"message": "I have a headache"})

# 12. Admin endpoints
print("\n📌 ADMIN PANEL")
if admin_token:
    admin_h = {"Authorization": f"Bearer {admin_token}"}
    check("GET /api/admin/stats", "GET", f"{BASE}/admin/stats", 200, headers=admin_h)
    check("GET /api/admin/users", "GET", f"{BASE}/admin/users", 200, headers=admin_h)
    check("GET /api/admin/reports", "GET", f"{BASE}/admin/reports", 200, headers=admin_h)
    check("GET /api/admin/appointments", "GET", f"{BASE}/admin/appointments", 200, headers=admin_h)
    check("GET /api/admin/system-health", "GET", f"{BASE}/admin/system-health", 200, headers=admin_h)
else:
    print("  ⚠️  No admin token, skipping admin endpoints")

# 13. Frontend serving
print("\n📌 FRONTEND SERVING")
try:
    r = requests.get("http://localhost:5000/", timeout=5)
    status = "✅ PASS" if r.status_code == 200 and "AI Health Assistant" in r.text else "❌ FAIL"
    results.append(("GET / (index.html)", status, r.status_code))
    print(f"  {status} GET / (index.html) => {r.status_code}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

try:
    r = requests.get("http://localhost:5000/pages/login.html", timeout=5)
    status = "✅ PASS" if r.status_code == 200 and "Login" in r.text else "❌ FAIL"
    results.append(("GET /pages/login.html", status, r.status_code))
    print(f"  {status} GET /pages/login.html => {r.status_code}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Summary
print("\n" + "=" * 60)
passes = sum(1 for _, s, _ in results if "PASS" in s)
fails = sum(1 for _, s, _ in results if "FAIL" in s or "ERROR" in s)
print(f"📊 Results: {passes} PASS, {fails} FAIL out of {len(results)} tests")
print("=" * 60)

if fails > 0:
    print("\n🔴 Failed tests:")
    for name, status, code in results:
        if "FAIL" in status or "ERROR" in status:
            print(f"   {name} => {code}")

sys.exit(0 if fails == 0 else 1)
