"""
Main routes - homepage, lobby, and room pages.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page - redirect to login or lobby."""
    if current_user.is_authenticated:
        return redirect(url_for('main.lobby'))
    return redirect(url_for('auth.login'))


@main_bp.route('/lobby')
@login_required
def lobby():
    """Lobby page - create or join rooms."""
    return render_template('lobby.html', username=current_user.username)


@main_bp.route('/room/<room_code>')
@login_required
def room(room_code):
    """Video room page - WebRTC, chat, whiteboard."""
    return render_template(
        'room.html',
        username=current_user.username,
        room_code=room_code
    )
