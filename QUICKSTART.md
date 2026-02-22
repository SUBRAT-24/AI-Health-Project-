"""
AI Health Assistant - Quick Start Guide
Fastest way to get the application running
"""

# ===== QUICK START (5 MINUTES) =====

## Step 1: Prerequisites Check
# Make sure you have:
# - Python 3.9+
# - MySQL 8.0+
# - Git
# Check versions:
python --version
mysql --version

# ===== STEP 2: Setup =====
# Clone/navigate to project
cd Project1

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# ===== STEP 3: Install Dependencies =====
pip install -r backend/requirements.txt

# ===== STEP 4: Database Setup =====

# Option A: Using MySQL directly
mysql -u root -p
CREATE DATABASE health_assistant;
USE health_assistant;
SOURCE database/schema.sql;
EXIT;

# Option B: Using init script
python backend/init_project.py

# ===== STEP 5: Configure =====
cp .env.example .env

# Edit .env file with your settings:
# - MYSQL_USER=root (or your user)
# - MYSQL_PASSWORD=your_password
# - JWT_SECRET_KEY=some-secret-key

# ===== STEP 6: Run Services =====

# Terminal 1 - Flask Backend
python backend/flask_app/__init__.py
# Output: Running on http://localhost:5000

# Terminal 2 - FastAPI Backend
cd backend
uvicorn fastapi_app.main:app --reload
# Output: Uvicorn running on http://localhost:8000

# Terminal 3 - Frontend
# Open browser to: http://localhost:8080/frontend/index.html

# ===== TEST THE APPLICATION =====

# 1. Sign up
# - Go to http://localhost:8080/frontend/pages/signup.html
# - Fill in details
# - Click Sign Up

# 2. Login
# - Use credentials you just created

# 3. Add health data
# - Go to Dashboard
# - Click "Add Health Data"
# - Enter some values

# 4. Book appointment
# - Go to Appointments
# - Click "Book Appointment"
# - Fill in doctor details

# 5. Try chatbot
# - Click chat icon (bottom right)
# - Ask a health question

# ===== DOCKER SETUP (OPTIONAL) =====

# If you want to use Docker instead:
docker-compose -f docker/docker-compose.yml up --build

# Access services:
# - Frontend: http://localhost:80
# - Flask: http://localhost:5000
# - FastAPI: http://localhost:8000

# ===== API TESTING =====

# Test Flask APIs using curl:

# 1. Signup
curl -X POST http://localhost:5000/api/auth/signup \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "password": "StrongPass123!"
  }'

# 2. Login
curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email": "john@example.com", "password": "StrongPass123!"}'

# 3. Get health data (use token from login)
curl -X GET http://localhost:5000/api/health/data \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# ===== TROUBLESHOOTING =====

# Issue: Port already in use
# Solution: Kill the process
# Windows: netstat -ano | findstr :5000
# Linux: lsof -i :5000

# Issue: Database connection error
# Solution: Check MySQL is running
# Windows: Services -> MySQL
# Linux: sudo service mysql status

# Issue: Module not found error
# Solution: Reinstall requirements
pip install -r backend/requirements.txt --force-reinstall

# Issue: .env file not found
# Solution: Copy it
cp .env.example .env

# ===== PROJECT STRUCTURE =====
# Project1/
# ├── frontend/          # HTML, CSS, JS
# ├── backend/
# │   ├── flask_app/     # Flask REST API
# │   ├── fastapi_app/   # FastAPI
# │   ├── ai_models/     # ML models
# │   └── utils/         # Helper functions
# ├── database/          # SQL schema
# ├── docker/            # Docker files
# ├── README.md          # Full documentation
# └── .env.example       # Config template

# ===== NEXT STEPS =====

# 1. Read README.md for full documentation
# 2. Read API_REFERENCE.py for all endpoints
# 3. Read CLOUD_DEPLOYMENT.md to deploy to cloud
# 4. Modify pages/ to add more features
# 5. Customize styles in css/ files

# ===== FEATURES YOU CAN TEST =====

# 1. Health Monitoring
#    - Add vitals (heart rate, BP, weight)
#    - View health history
#    - Get AI-powered insights

# 2. Doctor Appointments
#    - Book appointments
#    - Cancel appointments
#    - View appointment list

# 3. AI Chatbot
#    - Ask health questions
#    - Get instant responses
#    - 24/7 availability

# 4. Recommendations
#    - Get diet suggestions
#    - Get exercise routines
#    - Track medications

# 5. Medical Reports
#    - Upload reports
#    - AI analysis
#    - View history

# ===== ADMIN FEATURES =====

# View all users: GET /api/admin/users
# View statistics: GET /api/admin/statistics
# View system health: GET /api/admin/system-health

# ===== USEFUL LINKS =====

# Flask Docs: https://flask.palletsprojects.com/
# FastAPI Docs: https://fastapi.tiangolo.com/(going to auto docs at /docs)
# MySQL Docs: https://dev.mysql.com/doc/
# TensorFlow Docs: https://www.tensorflow.org/
# Docker Docs: https://docs.docker.com/

# ===== PRODUCTION DEPLOYMENT =====

# For AWS:
# 1. Create EC2 instance
# 2. Install Docker
# 3. Push Docker image to ECR
# 4. Run docker-compose
# See CLOUD_DEPLOYMENT.md for details

# ===== YOU'RE READY! =====

# The application is now set up and running.
# All features are functional and ready to use.
# See README.md for more detailed information.
# Happy coding! 🚀

"""
