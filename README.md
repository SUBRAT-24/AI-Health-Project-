# AI Health Assistant - Comprehensive Documentation

## 🏥 AI Health Assistant Platform

A comprehensive, AI-powered health management platform that combines cutting-edge technology with healthcare expertise to provide personalized health monitoring, recommendations, and doctor consultation services.

### 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [API Documentation](#api-documentation)
8. [AI Models](#ai-models)
9. [Database Structure](#database-structure)
10. [Deployment](#deployment)
11. [Contributing](#contributing)
12. [License](#license)

---

## 🎯 Project Overview

AI Health Assistant is an intelligent platform designed to:

- **Monitor Health**: Track vital signs and health metrics continuously
- **Provide Insights**: Use AI/ML to analyze health data and provide actionable insights
- **Recommend**: Suggest personalized diet plans, exercise routines, and medications
- **Connect**: Facilitate appointments with healthcare professionals
- **Support**: 24/7 AI-powered chatbot for health queries

---

## ✨ Features

### Core Features

1. **Health Monitoring**
   - Real-time vital signs tracking
   - Historical data visualization
   - Health status alerts

2. **Health Analysis**
   - AI-powered health assessment
   - Risk factor identification
   - Predictive health analytics

3. **Doctor Appointments**
   - Online appointment booking
   - Doctor search and filtering
   - Appointment reminders
   - Telemedicine support

4. **Medical Reports**
   - Report upload and storage
   - AI-based report analysis
   - Report history

5. **Personalized Recommendations**
   - Diet plans tailored to health profile
   - Exercise routines based on fitness level
   - Medication reminders and tracking

6. **AI Chatbot**
   - 24/7 health assistance
   - Symptom analysis
   - General health queries
   - Appointment scheduling

---

## 💻 Technology Stack

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive design with variables
- **JavaScript (Vanilla)**: Client-side interactions
- **Responsive Design**: Mobile-first approach

### Backend
- **Flask**: Python web framework for REST API
- **FastAPI**: Modern async API framework
- **Python**: Core backend language

### Database
- **MySQL**: Relational database
- **SQLAlchemy**: ORM for database operations

### AI/ML Technologies
- **TensorFlow**: Deep learning framework
- **Keras**: Neural networks
- **scikit-learn**: Machine learning algorithms
- **NLTK**: Natural language processing
- **Transformers**: Pre-trained NLP models (Hugging Face)
- **OpenCV**: Image processing for medical images
- **NumPy & Pandas**: Data manipulation

### DevOps & Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and web server
- **Redis**: Caching layer

### Cloud Deployment
- **AWS**: EC2, RDS, S3, CloudFront
- **Google Cloud**: Compute Engine, Cloud SQL
- **Azure**: Virtual Machines, Azure SQL

---

## 📦 Installation

### Prerequisites

- Python 3.9+
- MySQL 8.0+
- Node.js 14+
- Docker & Docker Compose (optional)
- Git

### Local Installation

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ai-health-assistant.git
cd ai-health-assistant
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

#### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

#### 4. Setup Database
```bash
# MySQL - Create database
mysql -u root -p < database/schema.sql

# Or use the initialization script
python backend/init_project.py
```

#### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

#### 6. Run Applications

**Terminal 1 - Flask Backend:**
```bash
python backend/flask_app/__init__.py
```

**Terminal 2 - FastAPI Backend:**
```bash
uvicorn backend.fastapi_app.main:app --reload
```

**Terminal 3 - Frontend:**
```bash
cd frontend
# Use Python's built-in server or any HTTP server
python -m http.server 8080
```

Access the application at: `http://localhost:8080`

### Docker Installation

```bash
# Build and run with Docker Compose
docker-compose -f docker/docker-compose.yml up --build

# Access services:
# Frontend: http://localhost:80
# Flask API: http://localhost:5000
# FastAPI: http://localhost:8000
```

---

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the root directory:

```env
# Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=health_assistant

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Flask
FLASK_ENV=development
SECRET_KEY=flask-secret-key

# FastAPI
FASTAPI_DEBUG=True

# API URLs
API_BACKEND_URL=http://localhost:5000
FRONTEND_URL=http://localhost:8080

# File Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Kaggle (for datasets)
KAGGLE_API_KEY=your-kaggle-api-key
```

---

## 🚀 Usage

### User Registration & Login

1. Click "Sign Up" on the homepage
2. Enter your details (name, email, phone, date of birth, gender)
3. Create a strong password
4. Log in with credentials

### Adding Health Data

1. Go to Dashboard
2. Click "Add Health Data"
3. Enter current metrics:
   - Heart rate (bpm)
   - Blood pressure (systolic/diastolic)
   - Weight (kg)
   - Temperature (°C)
   - Optional: Blood glucose, O2 saturation
4. Add notes (symptoms, food, etc.)
5. Submit

### Booking Appointments

1. Navigate to "Appointments" section
2. Click "Book Appointment"
3. Select doctor and date/time
4. Add reason for visit
5. Confirm booking

### Getting Recommendations

1. **Diet**: Go to Diet section → View personalized meal plans
2. **Exercise**: Go to Exercise section → View workout routines
3. All recommendations are based on your health profile

### Using Chatbot

1. Click chat icon at bottom right
2. Ask health-related questions
3. Get instant responses

---

## 📚 API Documentation

### Authentication Endpoints

#### User Registration
```http
POST /api/auth/signup
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "password": "StrongPass123!"
}
```

#### User Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "StrongPass123!"
}
```

### Health Endpoints

#### Update Health Metrics
```http
POST /api/health/update
Authorization: Bearer {token}
Content-Type: application/json

{
  "heart_rate": 72,
  "systolic": 120,
  "diastolic": 80,
  "weight": 70,
  "temperature": 37.0,
  "notes": "Feeling good"
}
```

#### Get Health Data
```http
GET /api/health/data?days=30
Authorization: Bearer {token}
```

#### Get Health Summary
```http
GET /api/health/summary
Authorization: Bearer {token}
```

### Appointment Endpoints

#### Book Appointment
```http
POST /api/appointments/book
Authorization: Bearer {token}
Content-Type: application/json

{
  "doctor_name": "Dr. Smith",
  "doctor_specialization": "Cardiologist",
  "appointment_date": "2026-02-20T10:00:00",
  "reason": "Routine checkup"
}
```

#### Get Appointments
```http
GET /api/appointments/list
Authorization: Bearer {token}
```

#### Cancel Appointment
```http
DELETE /api/appointments/{appointment_id}/cancel
Authorization: Bearer {token}
```

### Report Endpoints

#### Upload Report
```http
POST /api/reports/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: <medical_report_file>
report_type: blood_test
description: Monthly blood test
test_date: 2026-02-12
```

#### Get Reports
```http
GET /api/reports/list
Authorization: Bearer {token}
```

#### Analyze Report
```http
POST /api/reports/{report_id}/analyze
Authorization: Bearer {token}
```

---

## 🤖 AI Models

### 1. Health Analyzer (TensorFlow/Keras)
- Analyzes vital signs
- Predicts health conditions
- Generates health scores

### 2. NLP Processor (NLTK + Transformers)
- Symptom analysis from text
- Sentiment analysis
- Health entity extraction

### 3. CNN Disease Detector (TensorFlow)
- Medical image classification
- Disease detection
- Confidence scoring

### 4. LLM Chatbot (Transformers)
- Conversational AI
- Health advice generation
- Symptom inquiry

---

## 📊 Database Structure

### Key Tables

1. **users**: User accounts and profiles
2. **health_records**: Vital signs and measurements
3. **appointments**: Doctor appointments
4. **reports**: Medical reports and test results
5. **medicines**: Medication tracking
6. **diet_recommendations**: Personalized meal plans
7. **exercise_recommendations**: Workout routines
8. **chat_history**: Chatbot conversation logs

---

##cloud Deployment

### AWS Deployment

```bash
# 1. Create EC2 instance
# 2. Install Docker and Docker Compose
# 3. Clone repository
# 4. Run Docker Compose
docker-compose -f docker/docker-compose.yml up -d

# 5. Set up RDS for MySQL
# 6. Configure S3 for file uploads
# 7. Use CloudFront for CDN
# 8. Enable HTTPS with ACM/Route53
```

### Google Cloud Deployment

```bash
# 1. Create Compute Engine instance
# 2. Use Cloud SQL for database
# 3. Upload files to Cloud Storage
# 4. Configure Cloud Load Balancer
```

### Docker Hub Deployment

```bash
# Build and push Docker image
docker build -t yourusername/health-assistant .
docker push yourusername/health-assistant

# Pull and run
docker pull yourusername/health-assistant
docker run -d -p 80:80 yourusername/health-assistant
```

---

## 📝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🤝 Support

For support, email: support@healthassistant.com
Or visit: https://healthassistant.com/help

---

## 🙏 Acknowledgments

- TensorFlow and Keras teams
- NLTK and NLP community
- MySQL and SQLAlchemy teams
- Open source community

---

**Last Updated**: February 2026
**Version**: 1.0.0
