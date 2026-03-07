"""
Authentication routes - register, login, logout.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from models.user import register_user, verify_user

auth_bp = Blueprint('auth', __name__)

# Simple user object for Flask-Login (we don't use a full ORM)
class User:
    def __init__(self, username):
        self.id = username
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.lobby'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        success, message = register_user(username, password)
        if success:
            flash(message, 'success')
            login_user(User(username))
            return redirect(url_for('main.lobby'))
        flash(message, 'error')
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.lobby'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if verify_user(username, password):
            login_user(User(username))
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.lobby'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
