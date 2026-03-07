"""
Main Flask application - Real-time Communication Web App
Similar to a simple Zoom/Google Meet clone.

Run with: python app.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO

from config import SECRET_KEY, SOCKETIO_ASYNC_MODE
from routes.auth import auth_bp
from routes.main import main_bp
from routes.auth import User
from models.user import user_exists
from socket_events import register_socket_events


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by username (used by Flask-Login for session)."""
        if user_exists(user_id):
            return User(user_id)
        return None

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(main_bp, url_prefix='')

    return app


# Create app and SocketIO
app = create_app()
socketio = SocketIO(app, async_mode=SOCKETIO_ASYNC_MODE, cors_allowed_origins="*")

# Register Socket.IO event handlers
register_socket_events(socketio)


if __name__ == '__main__':
    print("Starting Real-time Communication Server...")
    print("Open http://127.0.0.1:5000 in your browser")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
