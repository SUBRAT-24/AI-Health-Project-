#!/usr/bin/env python
"""
WSGI entry point for Render deployment.
Gunicorn will import `app` from this file.

Usage (Render Start Command):
  gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
"""

import os
import sys

# ─── Fix encoding on some cloud envs ──────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ─── Path Setup ───────────────────────────────────────────────────────────────
# This file lives at project root (d:/Project1/) or backend/
# Ensure backend/ is on sys.path so `from flask_app import ...` works
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# ─── Create App ───────────────────────────────────────────────────────────────
from flask_app import create_flask_app
from flask_app.models import db

app = create_flask_app()

# Ensure tables exist on startup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
