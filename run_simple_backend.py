#!/usr/bin/env python
"""
Simple working Flask backend with models defined after db initialization
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import bcrypt

load_dotenv()

# Create Flask app - serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='/frontend')

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# ========================
# MODELS
# ========================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': str(self.date_of_birth) if self.date_of_birth else None,
            'gender': self.gender
        }


class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    heart_rate = db.Column(db.Integer)
    systolic = db.Column(db.Integer)
    diastolic = db.Column(db.Integer)
    weight = db.Column(db.Float)
    temperature = db.Column(db.Float)
    notes = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'heart_rate': self.heart_rate,
            'systolic': self.systolic,
            'diastolic': self.diastolic,
            'weight': self.weight,
            'temperature': self.temperature,
            'notes': self.notes,
            'timestamp': self.recorded_at.isoformat()
        }


class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_name = db.Column(db.String(120))
    specialization = db.Column(db.String(120))
    appointment_date = db.Column(db.Date)
    appointment_time = db.Column(db.String(10))
    status = db.Column(db.String(20), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_name': self.doctor_name,
            'specialization': self.specialization,
            'appointment_date': str(self.appointment_date),
            'appointment_time': self.appointment_time,
            'status': self.status
        }


# ========================
# ROUTES
# ========================

# Serve frontend index
@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

# API connectivity test (frontend calls this on load)
@app.route('/api/health/test', methods=['GET'])
def health_test():
    return jsonify({'status': 'ok', 'message': 'API is connected'}), 200


# ========================
# AUTHENTICATION ROUTES
# ========================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['email', 'password', 'name']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        user = User(
            email=data['email'],
            name=data['name'],
            phone=data.get('phone', ''),
            date_of_birth=datetime.fromisoformat(data.get('date_of_birth', '1990-01-01')).date() if data.get('date_of_birth') else None,
            gender=data.get('gender', 'other')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=24))
        
        return jsonify({
            'message': 'User registered successfully',
            'token': access_token,
            'user_id': user.id,
            'name': user.name,
            'email': user.email
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=24))
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user_id': user.id,
            'name': user.name,
            'email': user.email
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================
# HEALTH ROUTES
# ========================

@app.route('/api/health/update', methods=['POST'])
@jwt_required()
def update_health():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        health_record = HealthRecord(
            user_id=user_id,
            heart_rate=data.get('heart_rate'),
            systolic=data.get('systolic'),
            diastolic=data.get('diastolic'),
            weight=data.get('weight'),
            temperature=data.get('temperature'),
            notes=data.get('notes', '')
        )
        
        db.session.add(health_record)
        db.session.commit()
        
        return jsonify({'message': 'Health record updated', 'record': health_record.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/health/data', methods=['GET'])
@jwt_required()
def get_health_data():
    try:
        user_id = int(get_jwt_identity())
        records = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.recorded_at.desc()).limit(30).all()
        
        return jsonify({'records': [r.to_dict() for r in records]}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health/summary', methods=['GET'])
@jwt_required()
def get_health_summary():
    try:
        user_id = int(get_jwt_identity())
        latest = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.recorded_at.desc()).first()
        
        if latest:
            return jsonify({'summary': latest.to_dict()}), 200
        else:
            return jsonify({'summary': None}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================
# APPOINTMENT ROUTES
# ========================

@app.route('/api/appointments/book', methods=['POST'])
@jwt_required()
def book_appointment():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        appointment = Appointment(
            user_id=user_id,
            doctor_name=data.get('doctor_name'),
            specialization=data.get('specialization'),
            appointment_date=datetime.fromisoformat(data.get('appointment_date')).date() if data.get('appointment_date') else None,
            appointment_time=data.get('appointment_time'),
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({'message': 'Appointment booked', 'appointment': appointment.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/appointments/list', methods=['GET'])
@jwt_required()
def get_appointments():
    try:
        user_id = int(get_jwt_identity())
        appointments = Appointment.query.filter_by(user_id=user_id).order_by(Appointment.appointment_date.desc()).all()
        
        return jsonify({'appointments': [a.to_dict() for a in appointments]}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/appointments/<int:appointment_id>/cancel', methods=['DELETE'])
@jwt_required()
def cancel_appointment(appointment_id):
    try:
        user_id = int(get_jwt_identity())
        appointment = Appointment.query.filter_by(id=appointment_id, user_id=user_id).first()
        
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        appointment.status = 'cancelled'
        db.session.commit()
        
        return jsonify({'message': 'Appointment cancelled'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================
# DIET & EXERCISE ROUTES
# ========================

@app.route('/api/diet/recommendations', methods=['POST'])
def get_diet_recommendations():
    try:
        data = request.get_json()
        age = data.get('age', 30)
        health_condition = data.get('health_condition', 'normal')
        
        recommendations = {
            'diabetes': ['Low carb foods', 'Whole grains', 'Lean proteins'],
            'hypertension': ['Low sodium foods', 'Fresh fruits', 'Vegetables'],
            'normal': ['Balanced diet', 'Fresh fruits', 'Vegetables', 'Lean proteins']
        }
        
        return jsonify({
            'recommendations': recommendations.get(health_condition, recommendations['normal']),
            'condition': health_condition
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/exercise/recommendations', methods=['POST'])
def get_exercise_recommendations():
    try:
        data = request.get_json()
        fitness_level = data.get('fitness_level', 'beginner')
        
        recommendations = {
            'beginner': ['Walking 30 mins daily', 'Light yoga', 'Stretching'],
            'intermediate': ['Running 30 mins', 'Weight training', 'Swimming'],
            'advanced': ['HIIT training', 'Heavy lifting', 'Marathon prep']
        }
        
        return jsonify({
            'recommendations': recommendations.get(fitness_level, recommendations['beginner']),
            'fitness_level': fitness_level
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================
# CHATBOT ROUTES
# ========================

@app.route('/api/chatbot/message', methods=['POST'])
def chatbot_message():
    try:
        data = request.get_json()
        message = data.get('message', '').lower().strip()
        
        if not message:
            return jsonify({'response': 'Please enter a message.'}), 200
        
        # Simple NLP-like response system
        responses = {
            'headache': 'For a headache, try these remedies: (1) Rest in a quiet darkroom, (2) Stay hydrated - drink water, (3) Apply a cold/warm compress, (4) Take over-the-counter pain reliever if needed. If it persists beyond 72 hours, see a doctor.',
            'fever': 'For fever management: (1) Stay hydrated with water and electrolytes, (2) Rest and get plenty of sleep, (3) Take acetaminophen or ibuprofen per instructions, (4) Wear light clothing. Seek immediate medical help if temp exceeds 103°F or doesn\'t improve in 3 days.',
            'fatigue': 'To combat fatigue: (1) Get 7-9 hours of quality sleep daily, (2) Exercise regularly for 30 minutes, (3) Eat balanced meals with fruits, vegetables, proteins, (4) Stay hydrated, (5) Manage stress. If persistent, consult your doctor.',
            'cold': 'Common cold management: (1) Rest and hydrate thoroughly, (2) Use saline nasal drops, (3) Throat lozenges for sore throat, (4) Honey tea (if over 1 year), (5) Vitamin C foods. Most colds resolve in 7-10 days.',
            'cough': 'For cough relief: (1) Stay hydrated, (2) Use cough drops or lozenges, (3) Honey and ginger tea, (4) Humidify your room, (5) Avoid smoke/irritants. Persistent cough beyond 2 weeks needs medical evaluation.',
            'sore throat': 'Sore throat care: (1) Gargle with warm salt water, (2) Drink warm liquids like tea, (3) Use lozenges for numbing, (4) Rest your voice, (5) Take over-the-counter pain reliever. See doctor if causes difficulty swallowing.',
            'sleep': 'Sleep improvement tips: (1) Keep consistent sleep schedule, (2) Avoid screens 1 hour before bed, (3) Create dark, cool bedroom, (4) Exercise during day, (5) Limit caffeine after 2pm, (6) Try relaxation techniques. If insomnia persists, consult specialist.',
            'diet': 'Healthy diet guidelines: (1) Eat colorful fruits & vegetables daily, (2) Include lean proteins, (3) Choose whole grains, (4) Limit sugar & salt, (5) Drink 8+ glasses of water, (6) Plan meals ahead, (7) Practice portion control.',
            'exercise': 'Fitness recommendations: (1) 150 mins moderate cardio/week, (2) Strength training 2-3 times/week, (3) Flexibility work daily, (4) Start slowly if new, (5) Warm up before exercise, (6) Stay hydrated, (7) Listen to your body.',
            'stress': 'Stress management techniques: (1) Deep breathing exercises, (2) Meditation or mindfulness, (3) Regular exercise, (4) Adequate sleep, (5) Social connections, (6) Hobbies, (7) Progressive muscle relaxation. If overwhelming, seek professional help.',
            'weight': 'Weight management: (1) Balanced diet with portion control, (2) Regular exercise routine, (3) Track daily intake, (4) Drink plenty of water, (5) Get sufficient sleep, (6) Manage stress, (7) Consult nutritionist for personalized plan.',
            'blood pressure': 'Managing blood pressure: (1) Reduce sodium intake, (2) Regular exercise, (3) Maintain healthy weight, (4) Limit alcohol, (5) Manage stress, (6) Monitor regularly, (7) Take medications as prescribed. See doctor for personalized guidance.',
            'diabetes': 'Diabetes management: (1) Monitor blood sugar levels, (2) Eat balanced meals, (3) Exercise regularly, (4) Limit sugar & refined carbs, (5) Stay hydrated, (6) Take medications as prescribed, (7) Regular doctor checkups.',
            'appointment': 'To book an appointment: Click on "Appointments" in the menu, then "Book New Appointment". Select preferred date/time and doctor, then confirm.',
            'health record': 'View your health records: Go to "Health Tracking" or "Dashboard" to see your recorded metrics including heart rate, blood pressure, weight, and temperature history.',
            'medicine': 'Always consult your doctor or pharmacist about medications. I can provide general wellness information, but medical advice should come from licensed professionals.',
            'doctor': 'To find a doctor nearby: You can book appointments through our app, or search for specialists in your area online.',
        }
        
        # Determine best response
        response = responses.get('default', 'I\'m here to help! Ask me about health tips, diet, exercise, stress management, or general wellness. What would you like to know?')
        
        for key, value in responses.items():
            if key in message or key in message.replace(' ', ''):
                response = value
                break
        
        # Default response
        if response == responses.get('default'):
            if any(word in message for word in ['help', 'hi', 'hello', 'hey', 'start', 'info', '?']):
                response = 'I\'m your AI Health Assistant! I can help with: health tips, diet advice, exercise routines, stress management, sleep tips, medication info, and more. What would you like to know?'
            else:
                response = 'I can assist with health-related questions like headaches, fever, fatigue, diet, exercise, stress, sleep, and more. Feel free to ask me anything!'
        
        return jsonify({'response': response}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================
# ERROR HANDLERS
# ========================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ========================
# MAIN
# ========================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("\n" + "="*60)
        print("*** AI Health Assistant - Flask Backend (Simplified) ***")
        print("="*60)
        print("[OK] Database initialized")
        print("[OK] Tables created")
        print("\n[INFO] API running at http://localhost:5000")
        print("[INFO] Health check: http://localhost:5000/health")
        print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
