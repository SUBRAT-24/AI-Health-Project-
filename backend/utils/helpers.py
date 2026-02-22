import hashlib
import secrets
from datetime import datetime, timedelta
import re

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hash_value: str) -> bool:
    """Verify password against hash"""
    return hash_value == hash_password(password)

def generate_token(length: int = 32) -> str:
    """Generate secure random token"""
    return secrets.token_hex(length)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def validate_password_strength(password: str) -> dict:
    """Validate password strength"""
    strength = {
        'score': 0,
        'issues': []
    }
    
    if len(password) < 8:
        strength['issues'].append('Password must be at least 8 characters')
    else:
        strength['score'] += 1
    
    if not any(c.isupper() for c in password):
        strength['issues'].append('Password must contain uppercase letters')
    else:
        strength['score'] += 1
    
    if not any(c.islower() for c in password):
        strength['issues'].append('Password must contain lowercase letters')
    else:
        strength['score'] += 1
    
    if not any(c.isdigit() for c in password):
        strength['issues'].append('Password must contain numbers')
    else:
        strength['score'] += 1
    
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        strength['issues'].append('Password should contain special characters')
    else:
        strength['score'] += 1
    
    return strength

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI from weight and height"""
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)

def get_bmi_category(bmi: float) -> str:
    """Get BMI category"""
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 25:
        return 'Normal weight'
    elif bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'

def format_date(date_obj):
    """Format date to string"""
    return date_obj.strftime('%Y-%m-%d') if date_obj else None

def format_datetime(dt_obj):
    """Format datetime to string"""
    return dt_obj.strftime('%Y-%m-%d %H:%M:%S') if dt_obj else None

def get_age_from_dob(date_of_birth):
    """Calculate age from date of birth"""
    today = datetime.today()
    age = today.year - date_of_birth.year
    if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
        age -= 1
    return age

def get_time_difference(dt1, dt2):
    """Get human readable time difference"""
    diff = abs((dt2 - dt1).total_seconds())
    
    if diff < 60:
        return f'{int(diff)} seconds'
    elif diff < 3600:
        return f'{int(diff/60)} minutes'
    elif diff < 86400:
        return f'{int(diff/3600)} hours'
    else:
        return f'{int(diff/86400)} days'

def is_valid_blood_type(blood_type: str) -> bool:
    """Validate blood type"""
    valid_types = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
    return blood_type in valid_types

def calculate_caloric_need(age: int, gender: str, weight: float, height: float, activity_level: str) -> float:
    """Calculate daily caloric needs using Mifflin-St Jeor formula"""
    # BMR calculation
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Activity multiplier
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
    return bmr * multiplier
