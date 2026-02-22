"""Admin-only route decorator."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from flask_app.models import User


def admin_required(fn):
    """Require JWT and admin role."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        if getattr(user, 'role', None) != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper
