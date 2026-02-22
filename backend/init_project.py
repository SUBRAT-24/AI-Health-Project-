# AI Health Assistant - Project Initialization Script

import os
import sys
import subprocess
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        'uploads',
        'logs',
        'ml_models/pretrained',
        'data/datasets',
        'data/cache'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f'✓ Created directory: {directory}')

def create_env_file():
    """Create .env file from .env.example"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print('✓ Created .env file')
        else:
            print('✗ .env.example not found')
    else:
        print('✓ .env file already exists')

def install_dependencies():
    """Install Python dependencies"""
    print('\nInstalling Python dependencies...')
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], check=True)
        print('✓ Dependencies installed')
    except subprocess.CalledProcessError as e:
        print(f'✗ Error installing dependencies: {e}')
        return False
    return True

def initialize_database():
    """Initialize database"""
    print('\nInitializing database...')
    try:
        import mysql.connector
        from config import config
        
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            port=config.MYSQL_PORT
        )
        
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DATABASE}")
        cursor.execute(f"USE {config.MYSQL_DATABASE}")
        
        # Read and execute schema
        with open('database/schema.sql', 'r') as f:
            schema = f.read()
        
        for statement in schema.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print('✓ Database initialized')
        return True
    except Exception as e:
        print(f'✗ Error initializing database: {e}')
        return False

def download_ml_models():
    """Download pre-trained ML models"""
    print('\nDownloading ML models...')
    
    try:
        # This is a placeholder - in production, download actual models
        print('✓ ML models ready (placeholder)')
    except Exception as e:
        print(f'✗ Error downloading models: {e}')

def setup_nltk_data():
    """Download NLTK data"""
    print('\nSetting up NLTK data...')
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        print('✓ NLTK data downloaded')
    except Exception as e:
        print(f'Warning: {e}')

def main():
    """Main initialization function"""
    print('=' * 50)
    print('AI Health Assistant - Project Initialization')
    print('=' * 50)
    
    try:
        print('\n1. Creating directories...')
        create_directories()
        
        print('\n2. Setting up environment...')
        create_env_file()
        
        print('\n3. Installing dependencies...')
        if not install_dependencies():
            return False
        
        print('\n4. Setting up NLTK...')
        setup_nltk_data()
        
        print('\n5. Initializing database...')
        initialize_database()
        
        print('\n6. Downloading ML models...')
        download_ml_models()
        
        print('\n' + '=' * 50)
        print('✓ Initialization Complete!')
        print('=' * 50)
        print('\nNext steps:')
        print('1. Update .env file with your configuration')
        print('2. Run Flask: python backend/flask_app/__init__.py')
        print('3. Run FastAPI: uvicorn backend.fastapi_app.main:app --reload')
        print('4. Open frontend: http://localhost:8080')
        print('=' * 50)
        
        return True
    except Exception as e:
        print(f'\n✗ Initialization failed: {e}')
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
