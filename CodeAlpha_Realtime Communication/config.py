"""
Configuration settings for the Flask application.
Keeps all config in one place for easy modification.
"""

import os

# Secret key for session encryption - change in production!
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Use eventlet for async support (required for Flask-SocketIO)
SOCKETIO_ASYNC_MODE = 'eventlet'
