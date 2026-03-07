"""
User model - handles user storage and authentication.
Uses a simple in-memory store for simplicity (suitable for college project).
For production, you would use a database like SQLite or PostgreSQL.
"""

import hashlib
import json
import os

# Path to store user data (persists across restarts)
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.json')


def _ensure_data_dir():
    """Create data directory if it doesn't exist."""
    data_dir = os.path.dirname(DATA_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)


def _load_users():
    """Load users from JSON file. Returns empty dict if file doesn't exist."""
    _ensure_data_dir()
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_users(users):
    """Save users dict to JSON file."""
    _ensure_data_dir()
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def hash_password(password):
    """Hash password using SHA-256. For production, use bcrypt or argon2."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    """
    Register a new user. Returns (success: bool, message: str).
    """
    users = _load_users()
    if username in users:
        return False, "Username already taken"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 4:
        return False, "Password must be at least 4 characters"

    users[username] = {'password_hash': hash_password(password)}
    _save_users(users)
    return True, "Registration successful"


def verify_user(username, password):
    """
    Verify login credentials. Returns True if valid.
    """
    users = _load_users()
    if username not in users:
        return False
    return users[username]['password_hash'] == hash_password(password)


def user_exists(username):
    """Check if username exists."""
    return username in _load_users()
