from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta

# Import db and models first
from flask_sqlalchemy import SQLAlchemy
from flask_app.models import db

# Initialize extensions
jwt = JWTManager()

def create_flask_app():
    """Create and configure Flask application"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, '..', 'frontend')
    frontend_dir = os.path.abspath(frontend_dir)
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    
    # Load configuration
    from config import config
    app.config.from_object(config)
    
    # Initialize extensions with the app
    db.init_app(app)
    jwt.init_app(app)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints - DO THIS IN APP CONTEXT
    with app.app_context():
        db.create_all()  # Create tables first
        
        from flask_app.routes import auth, health, appointments, diet, exercise, reports, chatbot, admin
        
        app.register_blueprint(auth.bp)
        app.register_blueprint(health.bp)
        app.register_blueprint(appointments.bp)
        app.register_blueprint(diet.bp)
        app.register_blueprint(exercise.bp)
        app.register_blueprint(reports.bp)
        app.register_blueprint(chatbot.bp)
        app.register_blueprint(admin.bp)
    
    # Create upload folder
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy'}), 200

    # Serve frontend
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        if path.startswith('api/'):
            return jsonify({'error': 'Not found'}), 404
        f = os.path.join(app.static_folder, path)
        if os.path.isfile(f):
            return send_from_directory(app.static_folder, path)
        if '.' not in os.path.basename(path):
            return send_from_directory(app.static_folder, 'index.html')
        return jsonify({'error': 'Not found'}), 404

    return app

if __name__ == '__main__':
    app = create_flask_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
