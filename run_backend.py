#!/usr/bin/env python
"""
Flask Backend Startup Script
Initializes the database and starts the Flask development server
"""

import os
import sys

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from flask_app import create_flask_app, db

def main():
    """Start the Flask application"""
    print("\n" + "="*60)
    print("🚀 AI Health Assistant - Flask Backend")
    print("="*60 + "\n")
    
    # Create app
    print("📦 Initializing Flask application...")
    app = create_flask_app()
    
    # Create database tables
    with app.app_context():
        print("💾 Creating database tables...")
        db.create_all()
        print("✓ Database initialized")
    
    # Print startup info
    print("\n" + "="*60)
    print("✅ Backend Started Successfully!")
    print("="*60)
    print(f"🌐 API URL: http://localhost:5000/api")
    print(f"📍 Health Check: http://localhost:5000/health")
    print(f"📚 Full URL: http://0.0.0.0:5000")
    print(f"🗄️  Database: SQLite (health_assistant.db)")
    print("="*60 + "\n")
    
    # Start Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )

if __name__ == '__main__':
    main()
