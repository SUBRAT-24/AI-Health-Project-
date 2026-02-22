from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_app.models import db, Report
from werkzeug.utils import secure_filename
import os
from datetime import datetime

bp = Blueprint('reports', __name__, url_prefix='/api/reports')

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'txt', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_report():
    """Upload health report"""
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Create report record
        report = Report(
            user_id=user_id,
            report_type=request.form.get('report_type', 'general'),
            file_path=filename,
            description=request.form.get('description'),
            test_date=request.form.get('test_date'),
            status='uploaded'
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Report uploaded successfully',
            'report': report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/list', methods=['GET'])
@jwt_required()
def get_reports():
    """Get user's reports"""
    try:
        user_id = get_jwt_identity()
        
        reports = Report.query.filter_by(user_id=user_id).order_by(
            Report.upload_date.desc()
        ).all()
        
        return jsonify({
            'total': len(reports),
            'reports': [report.to_dict() for report in reports]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get specific report"""
    try:
        user_id = get_jwt_identity()
        report = Report.query.filter_by(
            id=report_id,
            user_id=user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        return jsonify(report.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:report_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Delete report"""
    try:
        user_id = get_jwt_identity()
        report = Report.query.filter_by(
            id=report_id,
            user_id=user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Delete file
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], report.file_path)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': 'Report deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:report_id>/analyze', methods=['POST'])
@jwt_required()
def analyze_report(report_id):
    """Analyze report using AI"""
    try:
        user_id = get_jwt_identity()
        report = Report.query.filter_by(
            id=report_id,
            user_id=user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Simulate AI analysis
        analysis = {
            'report_type': report.report_type,
            'analysis': f'Preliminary analysis of {report.report_type}',
            'findings': [
                'All values within normal range',
                'No abnormalities detected',
                'Recommend follow-up in 6 months'
            ],
            'recommendations': [
                'Continue current lifestyle',
                'Maintain regular check-ups',
                'Monitor for any changes'
            ],
            'confidence_score': 0.92
        }
        
        report.ai_analysis = str(analysis)
        report.status = 'analyzed'
        db.session.commit()
        
        return jsonify(analysis), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
