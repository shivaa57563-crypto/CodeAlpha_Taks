# Real-time Communication Web App

A beginner-friendly Zoom/Google Meet clone built with Python Flask, Flask-SocketIO, WebRTC, and vanilla JavaScript.

## Features

- **User Registration & Login** - Simple session-based authentication
- **Rooms** - Create or join rooms with a 6-character code
- **Video/Audio Calling** - Peer-to-peer WebRTC video chat
- **Text Chat** - Real-time chat inside the room
- **Whiteboard** - Collaborative drawing with HTML canvas
- **Screen Sharing** - Share your screen with other participants
- **Clean UI** - Simple, responsive design

## Project Structure

```
realtime communication project/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── socket_events.py       # Socket.IO event handlers
├── models/
│   └── user.py           # User model and auth logic
├── routes/
│   ├── auth.py           # Login, register, logout
│   └── main.py           # Lobby and room routes
├── templates/            # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── lobby.html
│   └── room.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js       # Room initialization
│       ├── webrtc.js     # Video/audio & screen share
│       ├── chat.js       # Text chat
│       └── whiteboard.js # Collaborative drawing
└── data/                 # User data (created on first run)
```

## How to Run

### 1. Install Python

Make sure you have Python 3.8 or higher installed.

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The server will start at **http://127.0.0.1:5000**

### 5. Test the App

1. Open two browser windows (or use incognito for a second user)
2. Register two different users
3. Log in as the first user and click **Create Room**
4. Copy the room code
5. Log in as the second user and enter the room code to **Join Room**
6. Both users should see each other's video and can chat, draw, and share screens

## Requirements

- Modern browser with WebRTC support (Chrome, Firefox, Edge, Safari)
- Camera and microphone permissions
- HTTPS or localhost for camera access (browsers require secure context)

## Error Handling

- **Connection issues**: The app shows error messages for failed connections
- **Media permissions**: If camera/mic access is denied, an error message is displayed
- **Room not found**: Users can join any room code; rooms are created when the first person creates one

## Notes for College Projects

- Code is well-commented and modular
- No advanced frameworks - just Flask, vanilla JS, and WebRTC
- User data is stored in `data/users.json` (simple JSON file)
- For production, replace with a proper database and use bcrypt for passwords

## License

Free to use for educational purposes.
