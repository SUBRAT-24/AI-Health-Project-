"""
AI Health Assistant - API Reference Documentation
"""

# API Base URLs
FLASK_API = "http://localhost:5000/api"
FASTAPI_API = "http://localhost:8000/api"

# Authentication Endpoints
ENDPOINTS = {
    "auth": {
        "signup": "POST /auth/signup",
        "login": "POST /auth/login",
        "profile": "GET /auth/profile",
        "update_profile": "PUT /auth/profile",
        "change_password": "POST /auth/change-password"
    },
    
    "health": {
        "update_metrics": "POST /health/update",
        "get_data": "GET /health/data",
        "get_summary": "GET /health/summary",
        "analyze": "POST /health/analyze"
    },
    
    "appointments": {
        "book": "POST /appointments/book",
        "list": "GET /appointments/list",
        "get_detail": "GET /appointments/{id}",
        "update": "PUT /appointments/{id}/update",
        "cancel": "DELETE /appointments/{id}/cancel",
        "upcoming": "GET /appointments/upcoming"
    },
    
    "reports": {
        "upload": "POST /reports/upload",
        "list": "GET /reports/list",
        "get_detail": "GET /reports/{id}",
        "delete": "DELETE /reports/{id}/delete",
        "analyze": "POST /reports/{id}/analyze"
    },
    
    "diet": {
        "recommendations": "POST /diet/recommendations",
        "meal_plan": "POST /diet/meal-plan"
    },
    
    "exercise": {
        "recommendations": "POST /exercise/recommendations",
        "log": "POST /exercise/log",
        "history": "GET /exercise/history"
    },
    
    "chatbot": {
        "message": "POST /chatbot/message",
        "tips": "GET /chatbot/health-tips",
        "faq": "GET /chatbot/faq"
    },
    
    "admin": {
        "users": "GET /admin/users",
        "user_detail": "GET /admin/users/{id}",
        "statistics": "GET /admin/statistics",
        "data_management": "POST /admin/data-management",
        "system_health": "GET /admin/system-health"
    }
}

# Request/Response Examples

SIGNUP_REQUEST = {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "password": "StrongPass123!"
}

LOGIN_REQUEST = {
    "email": "john@example.com",
    "password": "StrongPass123!"
}

LOGIN_RESPONSE = {
    "message": "Login successful",
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user_id": 1,
    "name": "John Doe",
    "email": "john@example.com"
}

HEALTH_METRICS_REQUEST = {
    "heart_rate": 72,
    "systolic": 120,
    "diastolic": 80,
    "weight": 70.5,
    "temperature": 37.0,
    "blood_glucose": 100,
    "oxygen_saturation": 98,
    "notes": "Feeling great"
}

APPOINTMENT_REQUEST = {
    "doctor_name": "Dr. Smith",
    "doctor_specialization": "Cardiologist",
    "appointment_date": "2026-02-20T10:00:00",
    "reason": "Routine checkup",
    "duration_minutes": 30
}

DIET_RECOMMENDATION_REQUEST = {
    "age": 30,
    "gender": "male",
    "health_condition": "normal",
    "height": 180,
    "weight": 75
}

EXERCISE_RECOMMENDATION_REQUEST = {
    "age": 30,
    "fitness_level": "intermediate",
    "health_condition": "normal",
    "goals": ["weight_loss", "endurance"]
}

CHATBOT_MESSAGE_REQUEST = {
    "message": "What should I eat for high blood pressure?"
}

# Error Responses

ERROR_401 = {
    "error": "Unauthorized",
    "code": 401
}

ERROR_404 = {
    "error": "Not found",
    "code": 404
}

ERROR_500 = {
    "error": "Internal server error",
    "code": 500
}

# HTTP Status Codes
STATUS_CODES = {
    200: "OK",
    201: "Created",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error"
}

# Authentication Headers
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer <your-jwt-token>"
}

# Rate Limiting (per minute)
RATE_LIMITS = {
    "default": 60,
    "auth": 10,
    "upload": 5
}

"""
Usage Examples:

# 1. Sign Up
curl -X POST http://localhost:5000/api/auth/signup \\
  -H "Content-Type: application/json" \\
  -d '{"name":"John","email":"john@example.com",...}'

# 2. Login
curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email":"john@example.com","password":"password"}'

# 3. Add Health Metrics
curl -X POST http://localhost:5000/api/health/update \\
  -H "Authorization: Bearer TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"heart_rate":72,"weight":70,...}'

# 4. Get Health Data
curl -X GET http://localhost:5000/api/health/data?days=30 \\
  -H "Authorization: Bearer TOKEN"

"""
