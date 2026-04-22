from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta

# Import db from models so it can be re-exported
from flask_app.models import db

# Initialize JWT extension (will be bound to app later)
jwt = JWTManager()


def create_flask_app():
    """Create and configure the Flask application (application factory pattern)."""
    # Resolve paths
    backend_dir = os.path.dirname(os.path.abspath(__file__))           # .../backend/flask_app
    project_root = os.path.abspath(os.path.join(backend_dir, '..', '..'))  # d:/Project1
    frontend_dir = os.path.join(project_root, 'frontend')
    uploads_dir  = os.path.join(project_root, 'uploads')

    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.url_map.strict_slashes = False

    # -------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------
    import sys
    backend_path = os.path.join(project_root, 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    from config import config  # loads backend/config.py
    app.config.from_object(config)

    # Override a few settings to make sure they are always correct
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI',
        f"sqlite:///{os.path.join(project_root, 'instance', 'health_assistant.db')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    # Flask-JWT-Extended 4.x requires timedelta, NOT a plain integer
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['UPLOAD_FOLDER'] = uploads_dir
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'flask-secret-key')

    # -------------------------------------------------------------------
    # Extensions
    # -------------------------------------------------------------------
    db.init_app(app)
    jwt.init_app(app)

    # CORS – allow all origins for /api/* (for dev; tighten in production)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # -------------------------------------------------------------------
    # Database & Blueprints (require app context)
    # -------------------------------------------------------------------
    with app.app_context():
        db.create_all()

        from flask_app.routes import auth, health, appointments, diet, exercise, reports, chatbot, admin

        app.register_blueprint(auth.bp)
        app.register_blueprint(health.bp)
        app.register_blueprint(appointments.bp)
        app.register_blueprint(diet.bp)
        app.register_blueprint(exercise.bp)
        app.register_blueprint(reports.bp)
        app.register_blueprint(chatbot.bp)
        app.register_blueprint(admin.bp)

    # -------------------------------------------------------------------
    # Upload folder
    # -------------------------------------------------------------------
    os.makedirs(uploads_dir, exist_ok=True)

    # -------------------------------------------------------------------
    # Error handlers
    # -------------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    # -------------------------------------------------------------------
    # Health-check endpoint
    # -------------------------------------------------------------------
    @app.route('/api/healthcheck', methods=['GET'])
    def healthcheck():
        return jsonify({'status': 'healthy', 'message': 'AI Health Assistant API is running'}), 200

    # -------------------------------------------------------------------
    # Static file serving (serve frontend)
    # -------------------------------------------------------------------
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        # Never intercept API paths
        if path.startswith('api/'):
            return jsonify({'error': 'Not found'}), 404
        full_path = os.path.join(app.static_folder, path)
        if os.path.isfile(full_path):
            return send_from_directory(app.static_folder, path)
        # SPA fallback for routes without extensions
        if '.' not in os.path.basename(path):
            return send_from_directory(app.static_folder, 'index.html')
        return jsonify({'error': 'Not found'}), 404

    return app


if __name__ == '__main__':
    app = create_flask_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
