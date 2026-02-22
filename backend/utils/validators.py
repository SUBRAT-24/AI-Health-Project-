from utils.helpers import validate_email, validate_phone, validate_password_strength

class ValidationError(Exception):
    """Custom validation exception"""
    pass

def validate_user_signup(data):
    """Validate user signup data"""
    errors = []
    
    # Name validation
    if not data.get('name') or len(data['name']) < 2:
        errors.append('Name must be at least 2 characters')
    
    # Email validation
    if not data.get('email'):
        errors.append('Email is required')
    elif not validate_email(data['email']):
        errors.append('Invalid email format')
    
    # Phone validation
    if not data.get('phone'):
        errors.append('Phone number is required')
    elif not validate_phone(data['phone']):
        errors.append('Invalid phone format')
    
    # Date of birth validation
    if not data.get('date_of_birth'):
        errors.append('Date of birth is required')
    
    # Gender validation
    if not data.get('gender') or data['gender'] not in ['male', 'female', 'other']:
        errors.append('Invalid gender')
    
    # Password validation
    if not data.get('password'):
        errors.append('Password is required')
    else:
        strength = validate_password_strength(data['password'])
        if strength['score'] < 3:
            errors.extend(strength['issues'])
    
    return errors

def validate_health_record(data):
    """Validate health record data"""
    errors = []
    
    # Heart rate
    if data.get('heart_rate') is not None:
        if not isinstance(data['heart_rate'], int) or data['heart_rate'] < 0 or data['heart_rate'] > 220:
            errors.append('Invalid heart rate')
    
    # Blood pressure
    if data.get('systolic') is not None:
        if not isinstance(data['systolic'], int) or data['systolic'] < 0 or data['systolic'] > 300:
            errors.append('Invalid systolic pressure')
    
    if data.get('diastolic') is not None:
        if not isinstance(data['diastolic'], int) or data['diastolic'] < 0 or data['diastolic'] > 200:
            errors.append('Invalid diastolic pressure')
    
    # Weight
    if data.get('weight') is not None:
        if not isinstance(data['weight'], (int, float)) or data['weight'] < 0 or data['weight'] > 500:
            errors.append('Invalid weight')
    
    # Temperature
    if data.get('temperature') is not None:
        if not isinstance(data['temperature'], (int, float)) or data['temperature'] < 30 or data['temperature'] > 45:
            errors.append('Invalid temperature')
    
    return errors

def validate_appointment(data):
    """Validate appointment data"""
    errors = []
    
    if not data.get('doctor_name') or len(data['doctor_name']) < 2:
        errors.append('Doctor name is required')
    
    if not data.get('appointment_date'):
        errors.append('Appointment date is required')
    
    if data.get('duration_minutes'):
        if not isinstance(data['duration_minutes'], int) or data['duration_minutes'] <= 0:
            errors.append('Invalid duration')
    
    return errors

def validate_medicine(data):
    """Validate medicine data"""
    errors = []
    
    if not data.get('name') or len(data['name']) < 2:
        errors.append('Medicine name is required')
    
    if not data.get('dosage') or len(data['dosage']) < 1:
        errors.append('Dosage is required')
    
    if not data.get('frequency') or len(data['frequency']) < 1:
        errors.append('Frequency is required')
    
    return errors
