from datetime import datetime
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' | 'admin'
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(10))
    verification_code_expires = db.Column(db.DateTime)
    height = db.Column(db.Float)  # in cm
    blood_type = db.Column(db.String(10))
    allergies = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_records = db.relationship('HealthRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='user', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='user', lazy=True, cascade='all, delete-orphan')
    medicines = db.relationship('Medicine', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'blood_type': self.blood_type,
            'height': self.height,
            'role': self.role or 'user',
            'is_active': self.is_active if self.is_active is not None else True,
            'email_verified': self.email_verified if self.email_verified is not None else False,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    heart_rate = db.Column(db.Integer)  # bpm
    systolic = db.Column(db.Integer)  # mmHg
    diastolic = db.Column(db.Integer)  # mmHg
    weight = db.Column(db.Float)  # kg
    temperature = db.Column(db.Float)  # Celsius
    blood_glucose = db.Column(db.Float)  # mg/dL
    oxygen_saturation = db.Column(db.Float)  # %
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'heart_rate': self.heart_rate,
            'systolic': self.systolic,
            'diastolic': self.diastolic,
            'weight': self.weight,
            'temperature': self.temperature,
            'blood_glucose': self.blood_glucose,
            'oxygen_saturation': self.oxygen_saturation,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat()
        }


class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_name = db.Column(db.String(120), nullable=False)
    doctor_specialization = db.Column(db.String(120))
    appointment_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    reason = db.Column(db.Text)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, confirmed, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'doctor_name': self.doctor_name,
            'doctor_specialization': self.doctor_specialization,
            'appointment_date': self.appointment_date.isoformat(),
            'duration_minutes': self.duration_minutes,
            'reason': self.reason,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_type = db.Column(db.String(120))  # blood_test, x_ray, ultrasound, etc.
    file_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    test_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='uploaded')  # uploaded, pending_review, approved, rejected, analyzed
    ai_analysis = db.Column(db.Text)  # AI-generated analysis
    
    def to_dict(self):
        ud = self.upload_date.isoformat() if self.upload_date else None
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_type': self.report_type,
            'file_path': self.file_path,
            'description': self.description,
            'upload_date': ud,
            'uploaded_at': ud,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'status': self.status,
            'ai_analysis': self.ai_analysis
        }


class Medicine(db.Model):
    __tablename__ = 'medicines'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(120))
    frequency = db.Column(db.String(120))  # once daily, twice daily, etc.
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    reason = db.Column(db.Text)
    side_effects = db.Column(db.Text)
    doctor_prescribed = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'reason': self.reason,
            'side_effects': self.side_effects,
            'doctor_prescribed': self.doctor_prescribed,
            'is_active': self.is_active
        }


class DietRecommendation(db.Model):
    __tablename__ = 'diet_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
    meal_type = db.Column(db.String(50))  # breakfast, lunch, dinner, snack
    calories = db.Column(db.Integer)
    proteins = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fats = db.Column(db.Float)
    ingredients = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)


class ExerciseRecommendation(db.Model):
    __tablename__ = 'exercise_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_name = db.Column(db.String(120), nullable=False)
    duration_minutes = db.Column(db.Integer)
    intensity = db.Column(db.String(50))  # low, moderate, high
    frequency = db.Column(db.String(120))
    description = db.Column(db.Text)
    calories_burned = db.Column(db.Integer)
    benefits = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)


class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # Appearance & localization
    theme = db.Column(db.String(20), default='light')           # light | dark
    language = db.Column(db.String(10), default='en')
    date_format = db.Column(db.String(20), default='DD/MM/YYYY')
    measurement_units = db.Column(db.String(10), default='metric')  # metric | imperial
    timezone = db.Column(db.String(50), default='Asia/Kolkata')

    # Personal preferences
    dietary_preference = db.Column(db.String(30), default='non-veg')  # vegetarian | vegan | non-veg
    fitness_level = db.Column(db.String(20), default='moderate')     # sedentary | moderate | active | athlete

    # Notification settings
    vital_alerts_enabled = db.Column(db.Boolean, default=True)
    alert_frequency = db.Column(db.String(20), default='immediate')   # immediate | daily | weekly
    notification_method = db.Column(db.String(20), default='dashboard')  # dashboard | email | sms
    appointment_reminder = db.Column(db.String(10), default='24h')    # 24h | 1h | 30m
    medicine_reminder = db.Column(db.Boolean, default=True)

    # Vital sign thresholds
    hr_min = db.Column(db.Integer, default=60)
    hr_max = db.Column(db.Integer, default=100)
    bp_sys_min = db.Column(db.Integer, default=90)
    bp_sys_max = db.Column(db.Integer, default=140)
    bp_dia_min = db.Column(db.Integer, default=60)
    bp_dia_max = db.Column(db.Integer, default=90)
    temp_min = db.Column(db.Float, default=36.0)
    temp_max = db.Column(db.Float, default=37.5)

    # Daily goals
    daily_steps_goal = db.Column(db.Integer, default=10000)
    daily_water_goal = db.Column(db.Integer, default=8)   # glasses
    daily_sleep_goal = db.Column(db.Integer, default=8)    # hours

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in ('id',)}


class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')   # general | bug | feature | feedback | billing
    priority = db.Column(db.String(20), default='medium')     # low | medium | high | urgent
    status = db.Column(db.String(20), default='open')         # open | in_progress | resolved | closed
    admin_reply = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'message': self.message,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'admin_reply': self.admin_reply,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class FAQArticle(db.Model):
    __tablename__ = 'faq_articles'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')  # general | account | health | appointments | billing
    sort_order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'sort_order': self.sort_order,
            'is_published': self.is_published,
        }


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
