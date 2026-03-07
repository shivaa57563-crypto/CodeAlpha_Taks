"""
Socket.IO event handlers for real-time signaling and chat.
Handles WebRTC signaling, room management, and chat messages.
"""

from flask import request
from flask_socketio import join_room, leave_room, emit

import string
import random

# In-memory store for rooms: {room_code: [list of user socket_ids]}
rooms = {}


def generate_room_code(length=6):
    """Generate a random room code (letters and digits)."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def register_socket_events(socketio):
    """Register all Socket.IO event handlers with the app."""

    @socketio.on('connect')
    def handle_connect():
        """Client connected - no auth required for connect."""
        pass

    @socketio.on('create_room')
    def handle_create_room():
        """Create a new room and return the room code."""
        room_code = generate_room_code()
        while room_code in rooms:
            room_code = generate_room_code()
        rooms[room_code] = []
        emit('room_created', {'room_code': room_code})

    @socketio.on('join_room')
    def handle_join_room(data):
        """
        Join a room. Data: {room_code, username}
        Used for both room validation and chat/whiteboard participation.
        Sends list of existing peers to the joiner for WebRTC setup.
        """
        room_code = data.get('room_code', '').upper()
        username = data.get('username', '')

        if not room_code:
            emit('error', {'message': 'Room code is required'})
            return

        # Create room if it doesn't exist (first joiner)
        if room_code not in rooms:
            rooms[room_code] = []

        join_room(room_code)
        rooms[room_code].append({'sid': request.sid, 'username': username})

        # Send list of existing peers (excluding self) for WebRTC mesh
        existing_peers = [p for p in rooms[room_code] if p['sid'] != request.sid]
        emit('room_joined', {
            'room_code': room_code,
            'peers': [{'sid': p['sid'], 'username': p['username']} for p in existing_peers]
        })
        # Notify others about the new peer
        emit('user_joined', {
            'sid': request.sid,
            'username': username
        }, room=room_code, include_self=False)

    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Leave a room. Data: {room_code}"""
        room_code = data.get('room_code', '')
        # Emit user_left BEFORE leave_room so others in room get notified
        if room_code:
            emit('user_left', {'sid': request.sid}, room=room_code)
        if room_code in rooms:
            rooms[room_code] = [u for u in rooms[room_code] if u['sid'] != request.sid]
            if not rooms[room_code]:
                del rooms[room_code]
        leave_room(room_code)

    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Broadcast chat message to room. Data: {room_code, username, message}"""
        room_code = data.get('room_code', '')
        username = data.get('username', '')
        message = data.get('message', '')
        if room_code:
            emit('chat_message', {
                'username': username,
                'message': message
            }, room=room_code)

    @socketio.on('whiteboard_draw')
    def handle_whiteboard_draw(data):
        """Forward whiteboard drawing to other users in room."""
        room_code = data.get('room_code', '')
        if room_code:
            emit('whiteboard_draw', data, room=room_code, include_self=False)

    @socketio.on('whiteboard_clear')
    def handle_whiteboard_clear(data):
        """Forward whiteboard clear to other users."""
        room_code = data.get('room_code', '')
        if room_code:
            emit('whiteboard_clear', data, room=room_code, include_self=False)

    # --- WebRTC Signaling ---
    @socketio.on('webrtc_offer')
    def handle_webrtc_offer(data):
        """Forward WebRTC offer to target peer."""
        emit('webrtc_offer', data, room=data.get('target_sid', ''))

    @socketio.on('webrtc_answer')
    def handle_webrtc_answer(data):
        """Forward WebRTC answer to target peer."""
        # target_sid is who should receive (the offerer)
        emit('webrtc_answer', {
            'answer': data.get('answer'),
            'target_sid': data.get('target_sid'),
            'from_sid': request.sid
        }, room=data.get('target_sid', ''))

    @socketio.on('webrtc_ice_candidate')
    def handle_webrtc_ice_candidate(data):
        """Forward ICE candidate to target peer."""
        emit('webrtc_ice_candidate', {
            'candidate': data.get('candidate'),
            'target_sid': data.get('target_sid'),
            'from_sid': request.sid
        }, room=data.get('target_sid', ''))
