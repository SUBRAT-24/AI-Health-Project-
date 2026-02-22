## Local Development Setup Guide

### Quick Start

#### 1. Prerequisites
```bash
Python 3.9+
MySQL 8.0+
Node.js 14+ (optional, for npm)
Git
```

#### 2. Clone & Setup
```bash
git clone <repository-url>
cd Project1
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

#### 3. Database Setup
```bash
# Create database
mysql -u root -p < database/schema.sql

# Or run initialization script
python backend/init_project.py
```

#### 4. Configuration
```bash
cp .env.example .env
# Edit .env with your settings
```

#### 5. Run Backend Services

**Terminal 1 - Flask:**
```bash
cd backend
python flask_app/__init__.py
# Runs on http://localhost:5000
```

**Terminal 2 - FastAPI:**
```bash
cd backend
uvicorn fastapi_app.main:app --reload
# Runs on http://localhost:8000
```

#### 6. Access Frontend
```bash
# Open in browser:
http://localhost:8080/frontend/index.html
```

---

## Docker Setup

### Build and Run
```bash
docker-compose -f docker/docker-compose.yml up --build

# Services:
# - Frontend: http://localhost:80
# - Flask API: http://localhost:5000
# - FastAPI: http://localhost:8000
# - Database: localhost:3306
# - Redis Cache: localhost:6379
```

### Stop Services
```bash
docker-compose -f docker/docker-compose.yml down
```

---

## Testing

### Run Tests
```bash
pytest backend/tests/
```

### Create Test Sample
```bash
python backend/tests/sample_data.py
```

---

## File Structure
```
Project1/
├── frontend/          # HTML, CSS, JS files
├── backend/
│   ├── flask_app/    # Flask routes and models
│   ├── fastapi_app/  # FastAPI endpoints
│   ├── ai_models/    # ML models (CNN, NLP, etc.)
│   └── utils/        # Helper functions
├── database/         # SQL schemas
├── docker/          # Docker configuration
└── deployment/      # Cloud deployment guides
```

---

## Troubleshooting

**Database Connection Error**
- Check MySQL is running
- Verify credentials in .env
- Ensure database is created

**Port Already in Use**
- Flask: `lsof -i :5000` then `kill -9 <PID>`
- FastAPI: `lsof -i :8000` then `kill -9 <PID>`

**Module Not Found**
- Activate virtual environment
- Reinstall requirements: `pip install -r backend/requirements.txt`

For more issues, check the main README.md
