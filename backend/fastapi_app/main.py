from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
from config import config

# Initialize FastAPI app
app = FastAPI(
    title="AI Health Assistant API",
    description="FastAPI backend for health monitoring and recommendations",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthMetrics(BaseModel):
    heart_rate: int = None
    systolic: int = None
    diastolic: int = None
    weight: float = None
    temperature: float = None
    blood_glucose: float = None
    oxygen_saturation: float = None
    notes: str = None


class AppointmentRequest(BaseModel):
    doctor_name: str
    doctor_specialization: str = None
    appointment_date: datetime
    reason: str = None
    duration_minutes: int = 30


class MedicineEntry(BaseModel):
    name: str
    dosage: str
    frequency: str
    start_date: str = None
    end_date: str = None
    reason: str = None


class RecommendationRequest(BaseModel):
    age: int = None
    gender: str = None
    health_condition: str = "normal"
    height: float = None
    weight: float = None


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# API Routes
@app.post("/api/health-metrics", tags=["Health"])
async def add_health_metrics(metrics: HealthMetrics):
    """Add health metrics via FastAPI"""
    return {
        "message": "Health metrics recorded",
        "data": metrics.dict(),
        "timestamp": datetime.utcnow()
    }


@app.get("/api/health-metrics/{user_id}", tags=["Health"])
async def get_health_metrics(user_id: int):
    """Get health metrics for a user"""
    return {
        "user_id": user_id,
        "metrics": [],
        "count": 0
    }


@app.post("/api/recommendations/diet", tags=["Recommendations"])
async def get_diet_recommendations(request: RecommendationRequest):
    """Get diet recommendations"""
    recommendations = {
        "breakfast": [
            {"item": "Oatmeal", "calories": 150, "benefits": "High in fiber"},
            {"item": "Fresh Fruits", "calories": 100, "benefits": "Rich in vitamins"}
        ],
        "lunch": [
            {"item": "Grilled Chicken", "calories": 200, "benefits": "Lean protein"},
            {"item": "Brown Rice", "calories": 150, "benefits": "Whole grains"}
        ],
        "dinner": [
            {"item": "Baked Salmon", "calories": 250, "benefits": "Omega-3 fatty acids"},
            {"item": "Steamed Vegetables", "calories": 50, "benefits": "Vitamins and minerals"}
        ],
        "daily_goals": {
            "calories": 2000,
            "proteins": 50,
            "carbs": 250,
            "fats": 65
        }
    }
    return recommendations


@app.post("/api/recommendations/exercise", tags=["Recommendations"])
async def get_exercise_recommendations(request: RecommendationRequest):
    """Get exercise recommendations"""
    fitness_level = "beginner"
    
    if request.age:
        fitness_level = "intermediate" if request.age < 50 else "beginner"
    
    recommendations = {
        "fitness_level": fitness_level,
        "daily_routine": [
            {
                "exercise": "Walking",
                "duration": 30,
                "intensity": "moderate",
                "calories_burned": 150
            },
            {
                "exercise": "Stretching",
                "duration": 10,
                "intensity": "low",
                "calories_burned": 30
            }
        ],
        "weekly_plan": [
            "Monday: Walking + Yoga",
            "Tuesday: Swimming",
            "Wednesday: Jogging",
            "Thursday: Strength training",
            "Friday: Cycling",
            "Saturday: Sports or group activity",
            "Sunday: Rest day"
        ]
    }
    return recommendations


@app.post("/api/upload-report", tags=["Reports"])
async def upload_health_report(file: UploadFile = File(...)):
    """Upload health report"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")
    
    # File processing logic would go here
    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "status": "processing"
    }


@app.get("/api/health-tips", tags=["Education"])
async def get_health_tips():
    """Get daily health tips"""
    tips = [
        "Drink 8 glasses of water daily",
        "Exercise for 30 minutes a day",
        "Eat plenty of vegetables",
        "Get 7-9 hours of sleep",
        "Manage stress through meditation",
        "Limit salt and sugar intake",
        "Maintain a healthy weight",
        "Regular health check-ups"
    ]
    return {"tips": tips}


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "AI Health Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "health_metrics": "/api/health-metrics",
            "diet_recommendations": "/api/recommendations/diet",
            "exercise_recommendations": "/api/recommendations/exercise",
            "health_tips": "/api/health-tips"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
