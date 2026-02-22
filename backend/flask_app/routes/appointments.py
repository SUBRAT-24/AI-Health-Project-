from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_app.models import db, Appointment
from datetime import datetime, timedelta

bp = Blueprint('appointments', __name__, url_prefix='/api/appointments')

@bp.route('/book', methods=['POST'])
@jwt_required()
def book_appointment():
    """Book a doctor appointment"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not all(k in data for k in ['doctor_name', 'appointment_date']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        appointment = Appointment(
            user_id=user_id,
            doctor_name=data['doctor_name'],
            doctor_specialization=data.get('doctor_specialization'),
            appointment_date=datetime.fromisoformat(data['appointment_date']),
            duration_minutes=data.get('duration_minutes', 30),
            reason=data.get('reason'),
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': appointment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/list', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get user's appointments"""
    try:
        user_id = get_jwt_identity()
        print(f'[DEBUG] Getting appointments for user {user_id}')
        
        appointments = Appointment.query.filter_by(user_id=user_id).order_by(
            Appointment.appointment_date.desc()
        ).all()
        
        print(f'[DEBUG] Found {len(appointments)} appointments')
        
        return jsonify({
            'total': len(appointments),
            'appointments': [apt.to_dict() for apt in appointments]
        }), 200
        
    except Exception as e:
        print(f'[DEBUG] Appointments error: {str(e)}')
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    """Get specific appointment"""
    try:
        user_id = get_jwt_identity()
        appointment = Appointment.query.filter_by(
            id=appointment_id, 
            user_id=user_id
        ).first()
        
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        return jsonify(appointment.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:appointment_id>/update', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Update appointment"""
    try:
        user_id = get_jwt_identity()
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            user_id=user_id
        ).first()
        
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        data = request.get_json()
        
        if 'appointment_date' in data:
            appointment.appointment_date = datetime.fromisoformat(data['appointment_date'])
        if 'status' in data:
            appointment.status = data['status']
        if 'notes' in data:
            appointment.notes = data['notes']
        if 'reason' in data:
            appointment.reason = data['reason']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment updated successfully',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:appointment_id>/cancel', methods=['DELETE'])
@jwt_required()
def cancel_appointment(appointment_id):
    """Cancel appointment"""
    try:
        user_id = get_jwt_identity()
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            user_id=user_id
        ).first()
        
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        appointment.status = 'cancelled'
        db.session.commit()
        
        return jsonify({'message': 'Appointment cancelled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_appointments():
    """Get upcoming appointments"""
    try:
        user_id = get_jwt_identity()
        now = datetime.utcnow()
        
        appointments = Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.appointment_date >= now,
            Appointment.status != 'cancelled'
        ).order_by(Appointment.appointment_date.asc()).all()
        
        return jsonify({
            'total': len(appointments),
            'appointments': [apt.to_dict() for apt in appointments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
