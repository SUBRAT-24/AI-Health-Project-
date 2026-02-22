from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from config import config

db = SQLAlchemy()

def get_database_url():
    """Get database connection URL"""
    return config.SQLALCHEMY_DATABASE_URI

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

def get_db_session():
    """Get database session"""
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    return Session()

def execute_query(query_file):
    """Execute SQL query from file"""
    try:
        conn = get_db_session()
        with open(query_file, 'r') as f:
            query = f.read()
        conn.execute(query)
        conn.commit()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

def backup_database():
    """Create database backup"""
    import subprocess
    timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_health_assistant_{timestamp}.sql'
    
    try:
        cmd = f"mysqldump -h {config.MYSQL_HOST} -u {config.MYSQL_USER} -p{config.MYSQL_PASSWORD} {config.MYSQL_DATABASE} > {backup_file}"
        subprocess.run(cmd, shell=True, check=True)
        return backup_file
    except Exception as e:
        print(f"Backup error: {e}")
        return None

def restore_database(backup_file):
    """Restore database from backup"""
    import subprocess
    
    try:
        cmd = f"mysql -h {config.MYSQL_HOST} -u {config.MYSQL_USER} -p{config.MYSQL_PASSWORD} {config.MYSQL_DATABASE} < {backup_file}"
        subprocess.run(cmd, shell=True, check=True)
        return True
    except Exception as e:
        print(f"Restore error: {e}")
        return False
