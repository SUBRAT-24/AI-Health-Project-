# AI Health Assistant — Project Overview

## Project Description

**AI Health Assistant** is a web-based personal health platform that helps users monitor their health, get personalized recommendations, book doctor appointments, and interact with an AI-powered health chatbot. It combines a simple, responsive frontend with a REST API backend and optional AI/ML capabilities for future enhancement.

---

## Objectives

1. **Centralized health management** — One place for users to track vitals (heart rate, blood pressure, weight, temperature, blood glucose, oxygen saturation), view history, and store medical reports.

2. **Personalized recommendations** — Diet suggestions and exercise plans based on user profile, age, health conditions, and fitness level.

3. **Doctor appointments** — Book, view, and cancel appointments with doctors; track status (scheduled, confirmed, completed, cancelled).

4. **AI health assistant** — 24/7 chatbot for general health advice (symptoms, diet, exercise, stress, sleep, etc.) using a keyword-based response system (extensible to NLP/LLM).

5. **Medicine tracking** — Record prescribed medicines, dosage, frequency, and reminders.

6. **Admin panel** — Admin login and dashboard for managing users and platform content (optional).

7. **Security and scalability** — JWT authentication, hashed passwords, CORS, and support for SQLite (dev) and MySQL (production).

---

## Technology Stack

### Frontend

| Technology | Purpose |
|------------|--------|
| **HTML5** | Semantic structure, forms, navigation |
| **CSS3** | Styling, flexbox/grid, animations, responsive layout |
| **Vanilla JavaScript (ES6+)** | UI logic, API calls, form validation, token handling |
| **No frontend framework** | No React/Vue/Angular; plain JS for simplicity |

- **Pages:** Landing (`index.html`), Login, Sign Up, Dashboard, Health Tracking, Appointments, Diet Suggestions, Exercise, Reports, Admin Login, Admin Dashboard  
- **Features:** Responsive design, toast notifications, chatbot widget, localStorage for JWT

### Backend

| Technology | Purpose |
|------------|--------|
| **Python 3.x** | Main backend language |
| **Flask** | Web framework, REST API, static file serving |
| **Flask-SQLAlchemy** | ORM for database models and migrations |
| **Flask-JWT-Extended** | JWT creation and protected routes |
| **Flask-CORS** | Cross-origin requests for frontend |
| **Bcrypt** | Password hashing |
| **python-dotenv** | Environment variables (DB, secrets) |
| **Werkzeug** | WSGI utilities (used by Flask) |

- **Entry points:** `run_simple_backend.py` (standalone Flask app) or `backend/flask_app` (modular Flask app with blueprints)  
- **API base:** `http://localhost:5000/api`  
- **Config:** `backend/config.py` — dev/test/production, SQLite or MySQL via `DATABASE_URI`

### Database

| Technology | Purpose |
|------------|--------|
| **SQLite** | Default development database (`health_assistant.db`) |
| **MySQL** | Optional production DB (via `mysql-connector-python`, env vars) |
| **SQLAlchemy** | Schema and queries; models: User, HealthRecord, Appointment, Report, Medicine, DietRecommendation, ExerciseRecommendation |

### AI / ML (Available in Stack)

| Technology | Purpose |
|------------|--------|
| **TensorFlow & Keras** | Deep learning (e.g. CNN for medical image analysis) |
| **PyTorch & torchvision** | Alternative DL / image models |
| **transformers (Hugging Face)** | NLP pipelines (symptom text, future chatbot upgrade) |
| **NLTK** | Text processing for health/NLP |
| **scikit-learn** | Classical ML (e.g. risk scoring, clustering) |
| **OpenCV & Pillow** | Image handling for report/scan analysis |
| **NumPy, Pandas, SciPy** | Data processing and analytics |
| **Plotly, Matplotlib, Seaborn** | Visualizations (e.g. health trends) |

- **Current behavior:** Chatbot uses **keyword-based** responses (no live CNN/NLP in production yet).  
- **Planned/extensible:** `backend/ai_models/` includes `cnn_detector.py` (CNN disease detection) and `nlp_processor.py` (transformers-based NLP) for future integration.

### DevOps & Testing

| Technology | Purpose |
|------------|--------|
| **pytest** | Backend unit/integration tests |
| **FastAPI & Uvicorn** | Optional alternative API server (in `requirements.txt`) |

---

## Architecture (High Level)

```
┌─────────────────┐     HTTP/JSON      ┌─────────────────┐
│   Frontend      │ ◄─────────────────► │   Backend       │
│   (HTML/CSS/JS) │   /api/*, JWT      │   (Flask)       │
└─────────────────┘                    └────────┬────────┘
                                                │
                                                ▼
                                        ┌───────────────┐
                                        │   Database    │
                                        │ SQLite/MySQL  │
                                        └───────────────┘
```

- Frontend is served by Flask from the `frontend/` folder (or opened as static files).  
- All data operations go through REST endpoints; protected routes require a valid JWT in the request.

---

## Key Features Summary

- **User auth:** Sign up, login, JWT, role (user/admin).  
- **Health tracking:** Record and view vitals and history.  
- **Appointments:** Book, list, cancel.  
- **Diet & exercise:** Recommendations by condition/fitness level.  
- **Reports:** Upload and store medical reports (with optional AI analysis field).  
- **Chatbot:** Health Q&A via keyword matching (upgradeable to NLP/LLM).  
- **Admin:** Separate login and dashboard for administrators.

---

## How to Run

1. **Backend:**  
   `python run_simple_backend.py`  
   → API at `http://localhost:5000`

2. **Frontend:**  
   Open `http://localhost:5000` (if using Flask to serve) or `frontend/index.html` via file/local server.

3. **First use:** Sign up on the landing page, then log in to access the dashboard and all features.

---

## Document References

- **FINAL_STATUS_REPORT.txt** — Detailed status, endpoints, testing, and troubleshooting.  
- **backend/requirements.txt** — All Python dependencies and versions.
