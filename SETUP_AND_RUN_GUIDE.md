# 🏥 AI Health Assistant — Setup & Run Guide

A complete, step-by-step guide to get the **AI Health Assistant** project running on your local machine.

---

## 📋 Table of Contents

1. [Prerequisites](#-1-prerequisites)
2. [Clone the Repository](#-2-clone-the-repository)
3. [Create a Virtual Environment](#-3-create-a-virtual-environment)
4. [Install Dependencies](#-4-install-dependencies)
5. [Configure Environment Variables](#-5-configure-environment-variables)
6. [Run the Application](#-6-run-the-application)
7. [Access the Application](#-7-access-the-application)
8. [Create an Admin User (Optional)](#-8-create-an-admin-user-optional)
9. [Using the Application](#-9-using-the-application)
10. [Project Structure Overview](#-10-project-structure-overview)
11. [API Endpoints Quick Reference](#-11-api-endpoints-quick-reference)
12. [Troubleshooting](#-12-troubleshooting)
13. [Stopping the Application](#-13-stopping-the-application)

---

## 🔧 1. Prerequisites

Make sure the following are installed on your system before starting:

| Software       | Version  | Download Link                                      |
| -------------- | -------- | -------------------------------------------------- |
| **Python**     | 3.9 or higher | [python.org/downloads](https://www.python.org/downloads/) |
| **pip**        | Latest   | Comes bundled with Python                          |
| **Git**        | Any      | [git-scm.com](https://git-scm.com/)               |

### Verify installations

Open a terminal (Command Prompt / PowerShell / Terminal) and run:

```bash
python --version
# Expected: Python 3.9.x or higher

pip --version
# Expected: pip 23.x or higher

git --version
# Expected: git version 2.x.x
```

> **Note:** On some systems you may need to use `python3` and `pip3` instead of `python` and `pip`.

---

## 📥 2. Clone the Repository

```bash
git clone https://github.com/SUBRAT-24/AI-Health-Project-.git
```

Then navigate into the project folder:

```bash
cd AI-Health-Project-
```

> **Already have the project?** Skip this step and navigate to your existing project directory.

---

## 🐍 3. Create a Virtual Environment

A virtual environment keeps the project dependencies isolated from your system Python.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

After activation, your terminal prompt will show `(venv)` at the beginning:

```
(venv) D:\AI-Health-Project->
```

---

## 📦 4. Install Dependencies

With the virtual environment **activated**, install all required Python packages:

```bash
pip install -r backend/requirements.txt
```

This will install Flask, SQLAlchemy, JWT authentication, AI/ML libraries, and all other dependencies.

### ⚡ Lightweight / Quick Install (Skip heavy AI/ML packages)

If you just want to run the core web application without the heavy AI/ML dependencies (TensorFlow, PyTorch, etc.), install only the essentials:

```bash
pip install Flask==3.0.0 Flask-CORS==4.0.0 Flask-SQLAlchemy==3.1.1 Flask-JWT-Extended==4.5.3 python-dotenv==1.0.0 bcrypt==4.1.1 Werkzeug==3.0.1
```

> This is useful for quick testing or if your machine has limited resources.

---

## ⚙️ 5. Configure Environment Variables

### Step 5a: Create the `.env` file

Create a file named `.env` in the **project root** directory:

### Windows (PowerShell)
```powershell
New-Item -Path .env -ItemType File
```

### macOS / Linux
```bash
touch .env
```

### Step 5b: Add the configuration

Open the `.env` file in any text editor and paste the following:

```env
# ──────────────────────────────────────────────
# Flask Settings
# ──────────────────────────────────────────────
FLASK_ENV=development
SECRET_KEY=your-flask-secret-key-change-this

# ──────────────────────────────────────────────
# JWT Authentication
# ──────────────────────────────────────────────
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# ──────────────────────────────────────────────
# Database (SQLite - default, no setup needed)
# ──────────────────────────────────────────────
# The app uses SQLite by default. The database file
# will be auto-created at: instance/health_assistant.db
#
# To use MySQL instead, uncomment and configure:
# DATABASE_URI=mysql+pymysql://root:password@localhost:3306/health_assistant

# ──────────────────────────────────────────────
# File Uploads
# ──────────────────────────────────────────────
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

> **Important:** For production use, change `SECRET_KEY` and `JWT_SECRET_KEY` to strong, random values.

> **SQLite is used by default** — no database server installation needed! The database file is automatically created when you first run the app.

---

## 🚀 6. Run the Application

With everything set up, start the backend server:

```bash
python run_backend.py
```

You should see output like this:

```
============================================================
🚀  AI Health Assistant - Flask Backend
============================================================
📦  Initialising Flask application...
✓   Database tables ready

============================================================
✅  Backend Started Successfully!
============================================================
🌐  API Base URL  : http://localhost:5000/api
🏥  Health Check  : http://localhost:5000/api/healthcheck
🖥️   Frontend      : http://localhost:5000
🗄️   Database      : SQLite → instance/health_assistant.db
📁  Uploads       : D:\AI-Health-Project-\uploads
============================================================
```

> **The server is now running!** Keep this terminal window open.

---

## 🌐 7. Access the Application

Open your web browser and navigate to:

| Page                  | URL                                                  |
| --------------------- | ---------------------------------------------------- |
| **🏠 Homepage**        | [http://localhost:5000](http://localhost:5000)        |
| **🔐 Login**           | [http://localhost:5000/pages/login.html](http://localhost:5000/pages/login.html) |
| **📝 Sign Up**         | [http://localhost:5000/pages/signup.html](http://localhost:5000/pages/signup.html) |
| **📊 Dashboard**       | [http://localhost:5000/pages/dashboard.html](http://localhost:5000/pages/dashboard.html) |
| **📅 Appointments**    | [http://localhost:5000/pages/appointments.html](http://localhost:5000/pages/appointments.html) |
| **❤️ Health Tracking** | [http://localhost:5000/pages/health-tracking.html](http://localhost:5000/pages/health-tracking.html) |
| **🥗 Diet Suggestions**| [http://localhost:5000/pages/diet-suggestions.html](http://localhost:5000/pages/diet-suggestions.html) |
| **🏋️ Exercise**        | [http://localhost:5000/pages/exercise.html](http://localhost:5000/pages/exercise.html) |
| **📄 Reports**         | [http://localhost:5000/pages/reports.html](http://localhost:5000/pages/reports.html) |
| **🔧 Admin Login**     | [http://localhost:5000/pages/admin-login.html](http://localhost:5000/pages/admin-login.html) |
| **🔧 Admin Dashboard** | [http://localhost:5000/pages/admin-dashboard.html](http://localhost:5000/pages/admin-dashboard.html) |
| **💚 API Health Check** | [http://localhost:5000/api/healthcheck](http://localhost:5000/api/healthcheck) |

---

## 👑 8. Create an Admin User (Optional)

To access the **Admin Dashboard**, you need to create an admin account.

Open a **new terminal window** (keep the server running in the first one), activate your venv, and run:

### With default credentials

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

python create_admin.py
```

This creates an admin with:
- **Email:** `admin@healthassistant.com`
- **Password:** `admin123`

### With custom credentials

```bash
python create_admin.py --email yourname@email.com --password YourSecurePassword --name "Your Name"
```

### Login as admin

Go to [http://localhost:5000/pages/admin-login.html](http://localhost:5000/pages/admin-login.html) and use the admin credentials.

---

## 🎯 9. Using the Application

### Step-by-Step User Workflow

```
1. Sign Up  →  Create a new account at /pages/signup.html
       ↓
2. Login    →  Log in with your credentials at /pages/login.html
       ↓
3. Dashboard →  View your health overview at /pages/dashboard.html
       ↓
4. Track     →  Add health metrics (heart rate, BP, weight, etc.)
       ↓
5. Book      →  Schedule doctor appointments
       ↓
6. Get Tips  →  Browse diet suggestions & exercise plans
       ↓
7. Reports   →  Upload and manage medical reports
       ↓
8. Chat      →  Use the AI chatbot (bottom-right icon) for health queries
```

### Feature Details

| Feature              | What You Can Do                                                        |
| -------------------- | ---------------------------------------------------------------------- |
| **Health Tracking**  | Record heart rate, blood pressure, weight, temperature, blood glucose  |
| **Appointments**     | Book, view, and cancel doctor appointments                            |
| **Diet Suggestions** | Get personalized meal plans based on your health profile               |
| **Exercise Plans**   | Get workout routines tailored to your fitness level                    |
| **Medical Reports**  | Upload, store, and analyze medical reports                             |
| **AI Chatbot**       | Ask health-related questions 24/7 via the chat widget                  |
| **Admin Panel**      | View user statistics, manage users, system health monitoring           |

---

## 📁 10. Project Structure Overview

```
AI-Health-Project-/
│
├── run_backend.py              ← 🚀 MAIN ENTRY POINT (run this!)
├── create_admin.py             ← 👑 Create admin users
├── .env                        ← ⚙️ Environment configuration (you create this)
├── .gitignore                  ← 🚫 Git ignore rules
│
├── backend/                    ← 🔧 Backend (Flask API)
│   ├── flask_app/
│   │   ├── __init__.py         ← App factory (creates Flask app)
│   │   ├── models/
│   │   │   └── __init__.py     ← Database models (User, HealthRecord, etc.)
│   │   ├── routes/
│   │   │   ├── auth.py         ← Login, Signup, Profile endpoints
│   │   │   ├── health.py       ← Health tracking endpoints
│   │   │   ├── appointments.py ← Appointment booking endpoints
│   │   │   ├── diet.py         ← Diet recommendation endpoints
│   │   │   ├── exercise.py     ← Exercise plan endpoints
│   │   │   ├── reports.py      ← Medical report endpoints
│   │   │   ├── chatbot.py      ← AI chatbot endpoints
│   │   │   └── admin.py        ← Admin panel endpoints
│   │   └── utils/
│   │       └── admin_decorator.py  ← Admin role checker
│   ├── config.py               ← Configuration management
│   └── requirements.txt        ← Python package dependencies
│
├── frontend/                   ← 🎨 Frontend (HTML/CSS/JS)
│   ├── index.html              ← Landing page
│   ├── css/
│   │   ├── style.css           ← Main stylesheet
│   │   └── dashboard-new.css   ← Dashboard styles
│   ├── js/
│   │   ├── main.js             ← Core JavaScript & API client
│   │   ├── auth.js             ← Login/Signup handlers
│   │   ├── dashboard.js        ← Dashboard logic
│   │   └── chatbot.js          ← Chatbot UI
│   └── pages/
│       ├── login.html          ← Login page
│       ├── signup.html         ← Registration page
│       ├── dashboard.html      ← User dashboard
│       ├── appointments.html   ← Appointments management
│       ├── health-tracking.html← Health metrics tracking
│       ├── diet-suggestions.html← Diet plans
│       ├── exercise.html       ← Exercise routines
│       ├── reports.html        ← Medical reports
│       ├── admin-login.html    ← Admin login page
│       └── admin-dashboard.html← Admin panel
│
├── instance/                   ← 📦 Auto-created at runtime
│   └── health_assistant.db     ← SQLite database file
│
├── uploads/                    ← 📎 User uploaded files
│
└── docs/
    ├── README.md               ← Project documentation
    ├── PROJECT_STRUCTURE.md    ← Detailed file manifest
    └── SETUP_AND_RUN_GUIDE.md  ← This file!
```

---

## 📡 11. API Endpoints Quick Reference

All API endpoints are prefixed with `/api`. Authentication-required endpoints need a JWT token in the `Authorization: Bearer <token>` header.

### 🔐 Authentication
| Method | Endpoint                  | Description          | Auth Required |
| ------ | ------------------------- | -------------------- | :-----------: |
| POST   | `/api/auth/signup`        | Register new user    |      ❌       |
| POST   | `/api/auth/login`         | Login & get token    |      ❌       |
| GET    | `/api/auth/profile`       | Get user profile     |      ✅       |
| PUT    | `/api/auth/profile`       | Update profile       |      ✅       |
| POST   | `/api/auth/change-password` | Change password    |      ✅       |

### ❤️ Health Tracking
| Method | Endpoint                  | Description              | Auth Required |
| ------ | ------------------------- | ------------------------ | :-----------: |
| POST   | `/api/health/update`      | Submit health metrics    |      ✅       |
| GET    | `/api/health/data`        | Get health history       |      ✅       |
| GET    | `/api/health/summary`     | Get health summary       |      ✅       |

### 📅 Appointments
| Method | Endpoint                              | Description          | Auth Required |
| ------ | ------------------------------------- | -------------------- | :-----------: |
| POST   | `/api/appointments/book`              | Book appointment     |      ✅       |
| GET    | `/api/appointments/list`              | List appointments    |      ✅       |
| DELETE | `/api/appointments/<id>/cancel`       | Cancel appointment   |      ✅       |

### 🥗 Diet & 🏋️ Exercise
| Method | Endpoint                          | Description              | Auth Required |
| ------ | --------------------------------- | ------------------------ | :-----------: |
| POST   | `/api/diet/recommendations`       | Get diet suggestions     |      ✅       |
| POST   | `/api/exercise/recommendations`   | Get exercise plans       |      ✅       |

### 📄 Reports
| Method | Endpoint                          | Description          | Auth Required |
| ------ | --------------------------------- | -------------------- | :-----------: |
| POST   | `/api/reports/upload`             | Upload a report      |      ✅       |
| GET    | `/api/reports/list`               | List all reports     |      ✅       |

### 🤖 Chatbot
| Method | Endpoint                      | Description          | Auth Required |
| ------ | ----------------------------- | -------------------- | :-----------: |
| POST   | `/api/chatbot/message`        | Send chat message    |      ✅       |
| GET    | `/api/chatbot/health-tips`    | Get health tips      |      ❌       |

### 💚 System
| Method | Endpoint                  | Description          | Auth Required |
| ------ | ------------------------- | -------------------- | :-----------: |
| GET    | `/api/healthcheck`        | API health check     |      ❌       |

---

## ❗ 12. Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'flask'`

**Cause:** Virtual environment is not activated or packages are not installed.

**Fix:**
```bash
# Activate venv first
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Then install packages
pip install -r backend/requirements.txt
```

---

### ❌ `Address already in use` / `Port 5000 is in use`

**Cause:** Another process is using port 5000.

**Fix (Windows):**
```powershell
# Find the process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace <PID> with the actual PID)
taskkill /PID <PID> /F
```

**Fix (macOS/Linux):**
```bash
lsof -i :5000
kill -9 <PID>
```

---

### ❌ `OperationalError: unable to open database file`

**Cause:** The `instance/` directory doesn't exist.

**Fix:**
```bash
mkdir instance
python run_backend.py
```

---

### ❌ `ImportError: cannot import name 'create_flask_app'`

**Cause:** Running from the wrong directory.

**Fix:** Make sure you run from the **project root** (the folder containing `run_backend.py`):
```bash
cd AI-Health-Project-
python run_backend.py
```

---

### ❌ TensorFlow / PyTorch installation errors

**Cause:** These are large AI/ML libraries that may not install on all systems.

**Fix:** Use the lightweight install (see [Step 4](#-lightweight--quick-install-skip-heavy-aiml-packages)). The core web application works without these AI/ML packages.

---

### ❌ `Access denied` or permission errors

**Fix (Windows):** Run the terminal as Administrator.

**Fix (macOS/Linux):** Use `sudo` if needed, or check folder permissions.

---

## 🛑 13. Stopping the Application

To stop the running server, press:

```
Ctrl + C
```

in the terminal where the server is running.

To **deactivate** the virtual environment:

```bash
deactivate
```

---

## 🔄 Quick Start Summary (TL;DR)

```bash
# 1. Clone
git clone https://github.com/SUBRAT-24/AI-Health-Project-.git
cd AI-Health-Project-

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate              # Windows
# source venv/bin/activate         # macOS/Linux

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Create .env file (copy the template from Step 5 above)

# 5. Run the app
python run_backend.py

# 6. Open browser
# → http://localhost:5000
```

---

**Last Updated:** April 2026  
**Version:** 1.0.0  
**Repository:** [github.com/SUBRAT-24/AI-Health-Project-](https://github.com/SUBRAT-24/AI-Health-Project-)
