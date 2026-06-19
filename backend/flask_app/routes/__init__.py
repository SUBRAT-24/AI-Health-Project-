"""
Flask application routes package
Contains all Flask route blueprints
"""

from . import auth
from . import health
from . import appointments
from . import diet
from . import exercise
from . import reports
from . import chatbot
from . import admin
from . import settings

__all__ = [
    'auth',
    'health',
    'appointments',
    'diet',
    'exercise',
    'reports',
    'chatbot',
    'admin',
    'settings'
]

