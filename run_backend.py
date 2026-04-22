#!/usr/bin/env python
"""
AI Health Assistant - Flask Backend Startup Script
Run this from the project root: python run_backend.py
"""

import os
import sys

# ─── Path Setup ────────────────────────────────────────────────────────────────
project_root = os.path.dirname(os.path.abspath(__file__))   # d:/Project1
backend_path = os.path.join(project_root, 'backend')

# Insert backend dir so that `from flask_app import ...` and `from config import ...` work
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# ─── App Factory ───────────────────────────────────────────────────────────────
from flask_app import create_flask_app
from flask_app.models import db


def main():
    print("\n" + "=" * 60)
    print("🚀  AI Health Assistant - Flask Backend")
    print("=" * 60)

    # Ensure instance directory exists for SQLite
    instance_dir = os.path.join(project_root, 'instance')
    os.makedirs(instance_dir, exist_ok=True)

    # Ensure uploads directory exists
    uploads_dir = os.path.join(project_root, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    print("📦  Initialising Flask application...")
    app = create_flask_app()

    # Tables are already created inside create_flask_app(); this is a safety net
    with app.app_context():
        db.create_all()
        print("✓   Database tables ready")

    print("\n" + "=" * 60)
    print("✅  Backend Started Successfully!")
    print("=" * 60)
    print(f"🌐  API Base URL  : http://localhost:5000/api")
    print(f"🏥  Health Check  : http://localhost:5000/api/healthcheck")
    print(f"🖥️   Frontend      : http://localhost:5000")
    print(f"🗄️   Database      : SQLite → instance/health_assistant.db")
    print(f"📁  Uploads       : {uploads_dir}")
    print("=" * 60 + "\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )


if __name__ == '__main__':
    main()
