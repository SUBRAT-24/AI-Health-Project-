"""Admin API: users, reports, appointments, stats. All routes require admin role."""
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_
from flask_app.models import db, User, HealthRecord, Appointment, Report
from flask_app.utils.admin_decorator import admin_required
import os

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ========================
# STATS & OVERVIEW
# ========================

@bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    """Platform statistics for admin dashboard."""
    try:
        pending_reports = Report.query.filter(
            Report.status.in_(['uploaded', 'pending_review'])
        ).count()
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_health_records': HealthRecord.query.count(),
            'total_appointments': Appointment.query.count(),
            'total_reports': Report.query.count(),
            'pending_reports': pending_reports,
            'scheduled_appointments': Appointment.query.filter_by(status='scheduled').count(),
            'completed_appointments': Appointment.query.filter_by(status='completed').count(),
            'cancelled_appointments': Appointment.query.filter_by(status='cancelled').count(),
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/statistics', methods=['GET'])
@admin_required
def get_statistics():
    """Alias for backward compatibility."""
    return get_stats()


@bp.route('/system-health', methods=['GET'])
@admin_required
def get_system_health():
    """System health status."""
    try:
        health_status = {
            'database': 'healthy',
            'api': 'healthy',
            'storage': 'healthy',
            'total_users': User.query.count(),
        }
        return jsonify(health_status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================
# USERS
# ========================

@bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """List all users with optional search."""
    try:
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        query = User.query
        if search:
            query = query.filter(
                or_(
                    User.email.ilike(f'%{search}%'),
                    User.name.ilike(f'%{search}%')
                )
            )
        query = query.order_by(User.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'total_users': pagination.total,
            'page': page,
            'per_page': per_page,
            'users': [u.to_dict() for u in pagination.items]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_details(user_id):
    """Get single user with counts."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        data = user.to_dict()
        data['total_health_records'] = len(user.health_records)
        data['total_appointments'] = len(user.appointments)
        data['total_reports'] = len(user.reports)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    """Set user is_active=False."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if getattr(user, 'role', None) == 'admin':
            return jsonify({'error': 'Cannot deactivate an admin'}), 400
        user.is_active = False
        db.session.commit()
        return jsonify({'message': 'User deactivated', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id):
    """Set user is_active=True."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user.is_active = True
        db.session.commit()
        return jsonify({'message': 'User activated', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<int:user_id>/delete', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Hard delete user (use with care)."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if getattr(user, 'role', None) == 'admin':
            return jsonify({'error': 'Cannot delete an admin'}), 400
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================
# REPORTS
# ========================

@bp.route('/reports', methods=['GET'])
@admin_required
def get_all_reports():
    """List all reports across users, optional status filter."""
    try:
        status_filter = request.args.get('status', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        query = Report.query.join(User).order_by(Report.upload_date.desc())
        if status_filter:
            query = query.filter(Report.status == status_filter)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = []
        for r in pagination.items:
            d = r.to_dict()
            d['user_name'] = r.user.name if r.user else None
            d['user_email'] = r.user.email if r.user else None
            items.append(d)
        return jsonify({
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'reports': items
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/reports/<int:report_id>', methods=['GET'])
@admin_required
def get_report_detail(report_id):
    """Get single report with user info."""
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        d = report.to_dict()
        d['user_name'] = report.user.name if report.user else None
        d['user_email'] = report.user.email if report.user else None
        return jsonify(d), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/reports/<int:report_id>/approve', methods=['POST'])
@admin_required
def approve_report(report_id):
    """Set report status to approved."""
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        report.status = 'approved'
        db.session.commit()
        return jsonify({'message': 'Report approved', 'report': report.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/reports/<int:report_id>/reject', methods=['POST'])
@admin_required
def reject_report(report_id):
    """Set report status to rejected."""
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        report.status = 'rejected'
        db.session.commit()
        return jsonify({'message': 'Report rejected', 'report': report.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/reports/<int:report_id>/delete', methods=['DELETE'])
@admin_required
def delete_report(report_id):
    """Delete report and its file."""
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        filepath = os.path.join(upload_folder, report.file_path)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass
        db.session.delete(report)
        db.session.commit()
        return jsonify({'message': 'Report deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================
# APPOINTMENTS
# ========================

@bp.route('/appointments', methods=['GET'])
@admin_required
def get_all_appointments():
    """List all appointments with user info."""
    try:
        status_filter = request.args.get('status', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        query = Appointment.query.join(User).order_by(Appointment.appointment_date.desc())
        if status_filter:
            query = query.filter(Appointment.status == status_filter)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = []
        for a in pagination.items:
            d = a.to_dict()
            d['user_name'] = a.user.name if a.user else None
            d['user_email'] = a.user.email if a.user else None
            items.append(d)
        return jsonify({
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'appointments': items
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/appointments/<int:appointment_id>/reject', methods=['POST'])
@admin_required
def reject_appointment(appointment_id):
    """Cancel/reject appointment (admin)."""
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        appointment.status = 'cancelled'
        db.session.commit()
        return jsonify({'message': 'Appointment cancelled', 'appointment': appointment.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================
# LEGACY (data-management)
# ========================

@bp.route('/data-management', methods=['POST'])
@admin_required
def manage_data():
    """Placeholder for bulk actions."""
    try:
        data = request.get_json() or {}
        action = data.get('action')
        if action == 'bulk_import':
            return jsonify({'message': 'Data import started'}), 200
        elif action == 'export':
            return jsonify({'message': 'Data export prepared'}), 200
        elif action == 'cleanup':
            return jsonify({'message': 'Data cleanup completed'}), 200
        return jsonify({'error': 'Invalid action'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
