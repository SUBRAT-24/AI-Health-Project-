#!/usr/bin/env python
"""
Flask Application Factory - Initializes the Flask app and all extensions
Uses SQLite for development to avoid MySQL connection issues
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_flask_app(config_name='development'):
    """
    Application factory for Flask app creation
    
    Args:
        config_name: Configuration environment (development, testing, production)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Configure app based on environment
    if config_name == 'development':
        # Use SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_assistant.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours
        app.config['UPLOAD_FOLDER'] = 'uploads'
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    else:
        # Use MySQL for production
        mysql_user = os.getenv('MYSQL_USER', 'root')
        mysql_password = os.getenv('MYSQL_PASSWORD', '')
        mysql_host = os.getenv('MYSQL_HOST', 'localhost')
        mysql_port = os.getenv('MYSQL_PORT', '3306')
        mysql_db = os.getenv('MYSQL_DATABASE', 'health_assistant')
        
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}'
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400
        app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'message': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        return {'message': 'Internal server error'}, 500
    
    # Register blueprints
    from backend.flask_app.routes import auth, health, appointments, diet, exercise, reports, chatbot, admin
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(health.bp, url_prefix='/api/health')
    app.register_blueprint(appointments.bp, url_prefix='/api/appointments')
    app.register_blueprint(diet.bp, url_prefix='/api/diet')
    app.register_blueprint(exercise.bp, url_prefix='/api/exercise')
    app.register_blueprint(reports.bp, url_prefix='/api/reports')
    app.register_blueprint(chatbot.bp, url_prefix='/api/chatbot')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

# Create the app
app = create_flask_app('development')

if __name__ == '__main__':
    print("🚀 Starting Flask application...")
    print("📍 API running at http://localhost:5000")
    print("📚 API docs at http://localhost:5000/api/docs")
    app.run(host='0.0.0.0', port=5000, debug=True)
