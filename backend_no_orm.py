#!/usr/bin/env python
"""
Simple Flask backend using sqlite3 directly (no SQLAlchemy/ORM issues)
Provides all API endpoints for the health assistant application
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
import sqlite3
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import bcrypt
from functools import wraps

load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_assistant.db'
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
DATABASE = 'health_assistant.db'

# Initialize extensions
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ========================
# DATABASE INITIALIZATION
# ========================

def init_db():
    """Initialize the database with tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            date_of_birth DATE,
            gender TEXT,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Health records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            heart_rate INTEGER,
            systolic INTEGER,
            diastolic INTEGER,
            weight REAL,
            temperature REAL,
            blood_glucose REAL,
            oxygen_saturation REAL,
            notes TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            doctor_name TEXT NOT NULL,
            specialization TEXT,
            appointment_date TEXT,
            duration_minutes INTEGER DEFAULT 30,
            reason TEXT,
            status TEXT DEFAULT 'scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            report_type TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized")

def dict_from_row(row, columns):
    """Convert database row to dictionary"""
    if not row:
        return None
    return dict(zip(columns, row))

# ========================
# AUTHENTICATION ROUTES
# ========================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validation
        required = ['email', 'password', 'name', 'phone', 'date_of_birth', 'gender']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (data['email'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        cursor.execute('''
            INSERT INTO users (name, email, phone, date_of_birth, gender, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['email'], data['phone'], data['date_of_birth'], data['gender'], password_hash))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        # Generate token (identity must be a string)
        access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(hours=24))
        
        conn.close()
        
        return jsonify({
            'message': 'User created successfully',
            'token': access_token,
            'user_id': user_id,
            'name': data['name']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, email, password_hash FROM users WHERE email = ?', (data['email'],))
        row = cursor.fetchone()
        
        conn.close()
        
        if not row or not bcrypt.checkpw(data['password'].encode(), row[3].encode()):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token (identity must be a string)
        access_token = create_access_token(identity=str(row[0]), expires_delta=timedelta(hours=24))
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user_id': row[0],
            'name': row[1],
            'email': row[2]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = int(get_jwt_identity())  # Convert back to int
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, phone, date_of_birth, gender
            FROM users WHERE id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'User not found'}), 404
        
        user = {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'phone': row[3],
            'date_of_birth': row[4],
            'gender': row[5]
        }
        
        return jsonify(user), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================
# HEALTH ROUTES
# ========================

@app.route('/api/health/update', methods=['POST'])
@jwt_required()
def update_health():
    """Update health metrics"""
    try:
        user_id = int(get_jwt_identity())  # Convert back to int
        data = request.get_json()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO health_records (user_id, heart_rate, systolic, diastolic, weight, temperature, blood_glucose, oxygen_saturation, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('heart_rate'),
            data.get('systolic'),
            data.get('diastolic'),
            data.get('weight'),
            data.get('temperature'),
            data.get('blood_glucose'),
            data.get('oxygen_saturation'),
            data.get('notes')
        ))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'Health metrics updated successfully',
            'id': record_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health/data', methods=['GET'])
@jwt_required()
def get_health_data():
    """Get user health data"""
    try:
        user_id = int(get_jwt_identity())  # Convert back to int
        days = request.args.get('days', 30, type=int)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT id, user_id, heart_rate, systolic, diastolic, weight, temperature, blood_glucose, oxygen_saturation, notes, timestamp
            FROM health_records
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        ''', (user_id, start_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            records.append({
                'id': row[0],
                'user_id': row[1],
                'heart_rate': row[2],
                'systolic': row[3],
                'diastolic': row[4],
                'weight': row[5],
                'temperature': row[6],
                'blood_glucose': row[7],
                'oxygen_saturation': row[8],
                'notes': row[9],
                'timestamp': row[10]
            })
        
        return jsonify({
            'total_records': len(records),
            'records': records
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health/summary', methods=['GET'])
@jwt_required()
def get_health_summary():
    """Get health summary"""
    try:
        user_id = int(get_jwt_identity())  # Convert back to int
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get latest record
        cursor.execute('''
            SELECT heart_rate, systolic, diastolic, weight, temperature, blood_glucose, oxygen_saturation, timestamp
            FROM health_records
            WHERE user_id = ?
            ORDER BY timestamp DESC LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'message': 'No health records found'}), 200
        
        return jsonify({
            'latest_record': {
                'heart_rate': row[0],
                'blood_pressure': f"{row[1]}/{row[2]}" if row[1] and row[2] else None,
                'weight': row[3],
                'temperature': row[4],
                'blood_glucose': row[5],
                'oxygen_saturation': row[6],
                'timestamp': row[7]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================
# APPOINTMENTS ROUTES
# ========================

@app.route('/api/appointments/book', methods=['POST'])
@jwt_required()
def book_appointment():
    """Book an appointment"""
    try:
        user_id = int(get_jwt_identity())  # Convert back to int
        data = request.get_json()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO appointments (user_id, doctor_name, specialization, appointment_date, reason, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('doctor_name'),
            data.get('specialization'),
            data.get('appointment_date'),
            data.get('reason'),
            'scheduled'
        ))
        
        conn.commit()
        appointment_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'Appointment booked successfully',
            'id': appointment_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments/list', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get user appointments"""
    try:
        user_id = int(get_jwt_identity())  # Convert back to int
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, doctor_name, specialization, appointment_date, status, notes, created_at
            FROM appointments
            WHERE user_id = ?
            ORDER BY appointment_date DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        appointments = []
        for row in rows:
            appointments.append({
                'id': row[0],
                'doctor_name': row[1],
                'specialization': row[2],
                'appointment_date': row[3],
                'status': row[4],
                'notes': row[5],
                'created_at': row[6]
            })
        
        return jsonify(appointments), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments/<int:appointment_id>/update', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Update appointment"""
    try:
        user_id = int(get_jwt_identity())  # Convert back to int
        data = request.get_json()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE appointments 
            SET status = ?, notes = ?
            WHERE id = ? AND user_id = ?
        ''', (data.get('status'), data.get('notes'), appointment_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Appointment updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments/<int:appointment_id>/cancel', methods=['DELETE'])
@jwt_required()
def cancel_appointment(appointment_id):
    """Cancel appointment"""
    try:
        user_id = int(get_jwt_identity())  # Convert back to int
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE appointments 
            SET status = ?
            WHERE id = ? AND user_id = ?
        ''', ('cancelled', appointment_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Appointment cancelled successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================
# CHATBOT ROUTES
# ========================

@app.route('/api/chatbot/message', methods=['POST'])
def chatbot_message():
    """Handle chatbot message"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        # Simple chatbot response logic
        response_text = generate_health_advice(message)
        
        return jsonify({
            'response': response_text,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_health_advice(message):
    """Generate health advice based on message"""
    message_lower = message.lower()
    
    advice_map = {
        'heart': 'To maintain heart health, exercise regularly for 30 minutes daily, reduce salt intake, and manage stress.',
        'weight': 'Maintain healthy weight through balanced diet and regular exercise. Consult a doctor if needed.',
        'exercise': 'Regular exercise (30 min per day) improves overall health. Start gradually and stay consistent.',
        'diet': 'Eat a balanced diet with fruits, vegetables, whole grains, and lean proteins. Avoid processed foods.',
        'sleep': 'Get 7-9 hours of quality sleep daily. Maintain consistent sleep schedule.',
        'stress': 'Manage stress through meditation, exercise, and relaxation techniques. Talk to someone if overwhelmed.',
        'water': 'Drink at least 8 glasses of water daily for proper hydration and metabolism.',
    }
    
    for keyword, advice in advice_map.items():
        if keyword in message_lower:
            return advice
    
    return 'Hello! I\'m your AI Health Assistant. I can help with health information, appointments scheduling, and general health advice. How can I help you today?'

@app.route('/api/chatbot/health-tips', methods=['GET'])
def get_health_tips():
    """Get health tips"""
    tips = [
        'Drink at least 8 glasses of water daily',
        'Exercise for at least 30 minutes daily',
        'Get 7-9 hours of sleep each night',
        'Eat a balanced diet with plenty of fruits and vegetables',
        'Manage stress through meditation or yoga',
        'Visit your doctor for regular check-ups',
        'Avoid smoking and excessive alcohol',
        'Monitor your blood pressure regularly'
    ]
    
    return jsonify({'tips': tips}), 200

# ========================
# SYSTEM ROUTES
# ========================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({'status': 'ok', 'message': 'API is running'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ========================
# MAIN
# ========================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 AI Health Assistant - Flask Backend (No ORM)")
    print("="*60 + "\n")
    
    print("💾 Initializing database...")
    init_db()
    
    print("\n" + "="*60)
    print("✅ Backend Started Successfully!")
    print("="*60)
    print(f"🌐 API URL: http://localhost:5000/api")
    print(f"📍 Health Check: http://localhost:5000/api/health")
    print(f"📚 Full URL: http://0.0.0.0:5000")
    print(f"🗄️  Database: SQLite (health_assistant.db)")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
