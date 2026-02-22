from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from flask_app.models import db, User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validation
        if not all(k in data for k in ['email', 'password', 'name', 'phone', 'date_of_birth', 'gender']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User(
            email=data['email'],
            name=data['name'],
            phone=data['phone'],
            date_of_birth=datetime.fromisoformat(data['date_of_birth']).date(),
            gender=data['gender']
        )
        
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=24))
        
        return jsonify({
            'message': 'User created successfully',
            'token': access_token,
            'user_id': user.id,
            'name': user.name
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not getattr(user, 'is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Generate token
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=24))
        print(f'[DEBUG] Login successful for user {user.id}, token: {access_token[:20]}...')
        
        role = getattr(user, 'role', None) or 'user'
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'role': role
        }), 200
        
    except Exception as e:
        print(f'[DEBUG] Login error: {str(e)}')
        return jsonify({'error': str(e)}), 500


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            user.name = data['name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'height' in data:
            user.height = data['height']
        if 'blood_type' in data:
            user.blood_type = data['blood_type']
        if 'allergies' in data:
            user.allergies = data['allergies']
        if 'medical_history' in data:
            user.medical_history = data['medical_history']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': 'Old and new passwords required'}), 400
        
        if not user.check_password(data['old_password']):
            return jsonify({'error': 'Invalid old password'}), 401
        
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
