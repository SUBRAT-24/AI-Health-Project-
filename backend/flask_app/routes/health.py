from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_app.models import db, HealthRecord, User
from datetime import datetime, timedelta

bp = Blueprint('health', __name__, url_prefix='/api/health')

@bp.route('/test', methods=['GET'])
def test_health():
    """Test endpoint - no auth required"""
    try:
        return jsonify({'message': 'Health API is working'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/update', methods=['POST'])
@jwt_required()
def update_health():
    """Update health metrics"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        health_record = HealthRecord(
            user_id=user_id,
            heart_rate=data.get('heart_rate'),
            systolic=data.get('systolic'),
            diastolic=data.get('diastolic'),
            weight=data.get('weight'),
            temperature=data.get('temperature'),
            blood_glucose=data.get('blood_glucose'),
            oxygen_saturation=data.get('oxygen_saturation'),
            notes=data.get('notes', '')
        )
        
        db.session.add(health_record)
        db.session.commit()
        
        return jsonify({
            'message': 'Health metrics updated successfully',
            'record': health_record.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/data', methods=['GET'])
@jwt_required()
def get_health_data():
    """Get user health data"""
    try:
        user_id = get_jwt_identity()
        print(f'[DEBUG] Getting health data for user {user_id}')
        days = request.args.get('days', 30, type=int)
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        records = HealthRecord.query.filter_by(user_id=user_id).filter(
            HealthRecord.timestamp >= start_date
        ).order_by(HealthRecord.timestamp.desc()).all()
        
        print(f'[DEBUG] Found {len(records)} health records')
        
        return jsonify({
            'total_records': len(records),
            'records': [record.to_dict() for record in records]
        }), 200
        
    except Exception as e:
        print(f'[DEBUG] Health data error: {str(e)}')
        return jsonify({'error': str(e)}), 500


@bp.route('/summary', methods=['GET'])
@jwt_required()
def get_health_summary():
    """Get health summary"""
    try:
        user_id = get_jwt_identity()
        
        # Get latest record
        latest = HealthRecord.query.filter_by(user_id=user_id).order_by(
            HealthRecord.timestamp.desc()
        ).first()
        
        if not latest:
            return jsonify({'error': 'No health data found'}), 404
        
        # Calculate statistics
        records = HealthRecord.query.filter_by(user_id=user_id).all()
        
        if not records:
            return jsonify({'error': 'No health data found'}), 404
        
        heart_rates = [r.heart_rate for r in records if r.heart_rate]
        weights = [r.weight for r in records if r.weight]
        temperatures = [r.temperature for r in records if r.temperature]
        
        summary = {
            'latest_record': latest.to_dict(),
            'statistics': {
                'heart_rate': {
                    'latest': latest.heart_rate,
                    'average': sum(heart_rates) / len(heart_rates) if heart_rates else None,
                    'min': min(heart_rates) if heart_rates else None,
                    'max': max(heart_rates) if heart_rates else None
                },
                'weight': {
                    'latest': latest.weight,
                    'average': sum(weights) / len(weights) if weights else None,
                    'min': min(weights) if weights else None,
                    'max': max(weights) if weights else None
                },
                'temperature': {
                    'latest': latest.temperature,
                    'average': sum(temperatures) / len(temperatures) if temperatures else None
                }
            }
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_health():
    """Analyze health data using AI"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get user's latest health records
        records = HealthRecord.query.filter_by(user_id=user_id).order_by(
            HealthRecord.timestamp.desc()
        ).limit(10).all()
        
        if not records:
            return jsonify({'error': 'No health data found'}), 404
        
        # Basic health analysis
        analysis = {
            'health_status': 'Good',
            'recommendations': [],
            'alerts': []
        }
        
        # Check latest vitals
        latest = records[0]
        
        # Heart rate check
        if latest.heart_rate:
            if latest.heart_rate < 60:
                analysis['alerts'].append('Heart rate is lower than normal. Consider consulting a doctor.')
            elif latest.heart_rate > 100:
                analysis['alerts'].append('Heart rate is elevated. Try relaxation techniques.')
            else:
                analysis['recommendations'].append('Your heart rate is in normal range.')
        
        # Blood pressure check
        if latest.systolic and latest.diastolic:
            if latest.systolic >= 140 or latest.diastolic >= 90:
                analysis['alerts'].append('Blood pressure is high. Consult a doctor.')
                analysis['health_status'] = 'Critical'
            elif latest.systolic >= 130 or latest.diastolic >= 80:
                analysis['alerts'].append('Blood pressure is elevated. Monitor regularly.')
                analysis['health_status'] = 'Warning'
            else:
                analysis['recommendations'].append('Your blood pressure is normal.')
        
        # Temperature check
        if latest.temperature:
            if latest.temperature > 37.5:
                analysis['alerts'].append('You have a fever. Rest and stay hydrated.')
                analysis['health_status'] = 'Warning'
            else:
                analysis['recommendations'].append('Your temperature is normal.')
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
