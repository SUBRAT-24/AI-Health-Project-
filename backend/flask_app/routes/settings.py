"""
Settings & Help API Routes
Handles user preferences, profile updates, support tickets, FAQ,
email verification and password reset.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from flask_app.models import db, User
import uuid
import random


bp = Blueprint('settings', __name__, url_prefix='/api/settings')


# ─── PROFILE ────────────────────────────────────────────────────────────────────

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get full user profile for settings page"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        profile = user.to_dict()
        # Add extra fields for settings display
        profile['emergency_contact_name'] = getattr(user, 'emergency_contact_name', '') or ''
        profile['emergency_contact_phone'] = getattr(user, 'emergency_contact_phone', '') or ''
        profile['updated_at'] = user.updated_at.isoformat() if user.updated_at else None
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile information"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        updatable = ['name', 'phone', 'gender', 'height', 'blood_type', 'allergies', 'medical_history']
        for field in updatable:
            if field in data:
                setattr(user, field, data[field])

        if 'date_of_birth' in data and data['date_of_birth']:
            user.date_of_birth = datetime.fromisoformat(data['date_of_birth']).date()

        # Emergency contact fields (stored as JSON in medical_history or separate columns if available)
        if 'emergency_contact_name' in data:
            user.emergency_contact_name = data.get('emergency_contact_name', '')
        if 'emergency_contact_phone' in data:
            user.emergency_contact_phone = data.get('emergency_contact_phone', '')

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─── PREFERENCES ─────────────────────────────────────────────────────────────────

@bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get user preferences"""
    try:
        user_id = int(get_jwt_identity())
        from flask_app.models import UserPreferences
        prefs = UserPreferences.query.filter_by(user_id=user_id).first()

        if not prefs:
            # Return defaults
            return jsonify({
                'theme': 'light',
                'language': 'en',
                'date_format': 'DD/MM/YYYY',
                'measurement_units': 'metric',
                'dietary_preference': 'non-veg',
                'fitness_level': 'moderate',
                'timezone': 'Asia/Kolkata',
                'vital_alerts_enabled': True,
                'alert_frequency': 'immediate',
                'notification_method': 'dashboard',
                'appointment_reminder': '24h',
                'medicine_reminder': True,
                'hr_min': 60, 'hr_max': 100,
                'bp_sys_min': 90, 'bp_sys_max': 140,
                'bp_dia_min': 60, 'bp_dia_max': 90,
                'temp_min': 36.0, 'temp_max': 37.5,
                'daily_steps_goal': 10000,
                'daily_water_goal': 8,
                'daily_sleep_goal': 8,
            }), 200

        return jsonify(prefs.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """Update user preferences"""
    try:
        user_id = int(get_jwt_identity())
        from flask_app.models import UserPreferences
        data = request.get_json()

        prefs = UserPreferences.query.filter_by(user_id=user_id).first()
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.session.add(prefs)

        fields = [
            'theme', 'language', 'date_format', 'measurement_units',
            'dietary_preference', 'fitness_level', 'timezone',
            'vital_alerts_enabled', 'alert_frequency', 'notification_method',
            'appointment_reminder', 'medicine_reminder',
            'hr_min', 'hr_max', 'bp_sys_min', 'bp_sys_max',
            'bp_dia_min', 'bp_dia_max', 'temp_min', 'temp_max',
            'daily_steps_goal', 'daily_water_goal', 'daily_sleep_goal',
        ]
        for field in fields:
            if field in data:
                setattr(prefs, field, data[field])

        db.session.commit()
        return jsonify({'message': 'Preferences updated', 'preferences': prefs.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─── CHANGE PASSWORD ─────────────────────────────────────────────────────────────

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password with current password verification"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current and new passwords are required'}), 400

        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401

        if len(data['new_password']) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400

        user.set_password(data['new_password'])
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─── DATA EXPORT / ACCOUNT ──────────────────────────────────────────────────────

@bp.route('/export-data', methods=['GET'])
@jwt_required()
def export_data():
    """Export all user data (GDPR data portability)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        from flask_app.models import HealthRecord, Appointment, Report, Medicine

        data = {
            'profile': user.to_dict(),
            'health_records': [r.to_dict() for r in HealthRecord.query.filter_by(user_id=user_id).all()],
            'appointments': [a.to_dict() for a in Appointment.query.filter_by(user_id=user_id).all()],
            'reports': [r.to_dict() for r in Report.query.filter_by(user_id=user_id).all()],
            'medicines': [m.to_dict() for m in Medicine.query.filter_by(user_id=user_id).all()],
            'export_date': datetime.utcnow().isoformat(),
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """Request account deletion"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json() or {}
        if not data.get('password'):
            return jsonify({'error': 'Password required to confirm deletion'}), 400

        if not user.check_password(data['password']):
            return jsonify({'error': 'Password incorrect'}), 401

        user.is_active = False
        db.session.commit()
        return jsonify({'message': 'Account deactivated. Contact support to permanently delete data.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─── EMAIL VERIFICATION ──────────────────────────────────────────────────────────

@bp.route('/send-verification-code', methods=['POST'])
@jwt_required()
def send_verification_code():
    """Generate and 'send' a 6-digit email verification code"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.email_verified:
            return jsonify({'message': 'Email is already verified'}), 200

        code = str(random.randint(100000, 999999))
        user.verification_code = code
        user.verification_code_expires = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()

        # In production, send via SMTP. For dev, log to console.
        print(f'[EMAIL VERIFICATION] Code for {user.email}: {code}')

        return jsonify({
            'message': f'Verification code sent to {user.email}',
            'hint': f'(Dev mode) Your code is: {code}'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/verify-email', methods=['POST'])
@jwt_required()
def verify_email():
    """Verify email with the 6-digit code"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.email_verified:
            return jsonify({'message': 'Email is already verified'}), 200

        data = request.get_json()
        code = data.get('code', '').strip()
        if not code:
            return jsonify({'error': 'Verification code is required'}), 400

        if user.verification_code != code:
            return jsonify({'error': 'Invalid verification code'}), 400

        if user.verification_code_expires and datetime.utcnow() > user.verification_code_expires:
            return jsonify({'error': 'Verification code has expired. Request a new one.'}), 400

        user.email_verified = True
        user.verification_code = None
        user.verification_code_expires = None
        db.session.commit()

        return jsonify({'message': 'Email verified successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─── PASSWORD RESET (public — no JWT) ────────────────────────────────────────────

@bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    """Generate a reset token and 'email' it to the user"""
    try:
        data = request.get_json()
        email = (data.get('email') or '').strip().lower()
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            # Don't reveal if the email exists or not
            return jsonify({'message': 'If that email exists, a reset link has been sent.'}), 200

        from flask_app.models import PasswordResetToken

        token = uuid.uuid4().hex
        reset = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )
        db.session.add(reset)
        db.session.commit()

        reset_link = f'http://localhost:5000/pages/reset-password.html?token={token}'
        print(f'[PASSWORD RESET] Link for {email}: {reset_link}')

        return jsonify({
            'message': 'If that email exists, a reset link has been sent.',
            'hint': f'(Dev mode) Reset link: {reset_link}'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using a valid token"""
    try:
        data = request.get_json()
        token = (data.get('token') or '').strip()
        new_password = data.get('new_password', '')

        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400

        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        from flask_app.models import PasswordResetToken

        reset = PasswordResetToken.query.filter_by(token=token, is_used=False).first()
        if not reset:
            return jsonify({'error': 'Invalid or already used reset token'}), 400

        if datetime.utcnow() > reset.expires_at:
            return jsonify({'error': 'Reset token has expired. Request a new one.'}), 400

        user = User.query.get(reset.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.set_password(new_password)
        reset.is_used = True
        db.session.commit()

        return jsonify({'message': 'Password reset successfully! You can now log in.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─── SUPPORT TICKETS ─────────────────────────────────────────────────────────────


@bp.route('/support/tickets', methods=['GET'])
@jwt_required()
def get_tickets():
    """Get user's support tickets"""
    try:
        user_id = int(get_jwt_identity())
        from flask_app.models import SupportTicket
        tickets = SupportTicket.query.filter_by(user_id=user_id).order_by(SupportTicket.created_at.desc()).all()
        return jsonify({'tickets': [t.to_dict() for t in tickets]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/support/tickets', methods=['POST'])
@jwt_required()
def create_ticket():
    """Create a support ticket"""
    try:
        user_id = int(get_jwt_identity())
        from flask_app.models import SupportTicket
        data = request.get_json()

        if not data.get('subject') or not data.get('message'):
            return jsonify({'error': 'Subject and message are required'}), 400

        ticket = SupportTicket(
            user_id=user_id,
            subject=data['subject'],
            message=data['message'],
            category=data.get('category', 'general'),
            priority=data.get('priority', 'medium'),
        )
        db.session.add(ticket)
        db.session.commit()
        return jsonify({'message': 'Ticket created', 'ticket': ticket.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─── FAQ ─────────────────────────────────────────────────────────────────────────

@bp.route('/faq', methods=['GET'])
def get_faq():
    """Get FAQ articles (public endpoint)"""
    try:
        from flask_app.models import FAQArticle
        category = request.args.get('category')
        query = FAQArticle.query.filter_by(is_published=True)
        if category:
            query = query.filter_by(category=category)
        articles = query.order_by(FAQArticle.sort_order.asc()).all()
        return jsonify({'articles': [a.to_dict() for a in articles]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── FEEDBACK ────────────────────────────────────────────────────────────────────

@bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    """Submit feedback or feature request"""
    try:
        user_id = int(get_jwt_identity())
        from flask_app.models import SupportTicket
        data = request.get_json()

        if not data.get('message'):
            return jsonify({'error': 'Feedback message is required'}), 400

        ticket = SupportTicket(
            user_id=user_id,
            subject=data.get('subject', 'User Feedback'),
            message=data['message'],
            category='feedback',
            priority='low',
        )
        db.session.add(ticket)
        db.session.commit()
        return jsonify({'message': 'Feedback submitted. Thank you!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
