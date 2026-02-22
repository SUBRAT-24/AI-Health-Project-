import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    
    # Database - Use SQLite for development, MySQL for production
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'health_assistant')
    MYSQL_PORT = os.getenv('MYSQL_PORT', 3306)
    
    # Database URL - Default to SQLite, override in environment
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        "sqlite:///health_assistant.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DELTA = 3600  # 1 hour
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-flask-secret-key')
    
    # FastAPI
    FASTAPI_DEBUG = os.getenv('FASTAPI_DEBUG', False)
    
    # File Upload
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # AI Models
    MODEL_PATH = os.path.join(os.path.dirname(__file__), '../ml_models')
    KAGGLE_API_KEY = os.getenv('KAGGLE_API_KEY', '')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MYSQL_DATABASE = 'health_assistant_test'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/health_assistant_test"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'


# Select configuration based on environment
config_name = os.getenv('FLASK_ENV', 'development')
if config_name == 'testing':
    config = TestingConfig()
elif config_name == 'production':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()
