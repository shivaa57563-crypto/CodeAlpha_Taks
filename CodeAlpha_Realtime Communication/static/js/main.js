/**
 * Main entry point - Initializes socket connection and all room modules.
 * Runs when the room page loads.
 */

(function() {
    const roomCode = window.ROOM_CODE;
    const username = window.USERNAME;

    if (!roomCode || !username) {
        console.error('Missing room code or username');
        return;
    }

    const socket = io();

    socket.on('connect', () => {
        socket.emit('join_room', {
            room_code: roomCode,
            username: username
        });
    });

    socket.on('room_joined', () => {
        // All modules are initialized - room is ready
        console.log('Joined room:', roomCode);
    });

    socket.on('error', (data) => {
        alert(data.message || 'An error occurred');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });

    // Initialize modules
    WebRTC.init(socket, roomCode, username);
    Chat.init(socket, roomCode, username);
    Whiteboard.init(socket, roomCode);

    // Video controls
    document.getElementById('toggleMic')?.addEventListener('click', () => {
        const enabled = WebRTC.toggleMic();
        const btn = document.getElementById('toggleMic');
        btn.textContent = enabled ? '🎤' : '🔇';
        btn.title = enabled ? 'Mute' : 'Unmute';
    });

    document.getElementById('toggleCamera')?.addEventListener('click', () => {
        const enabled = WebRTC.toggleCamera();
        const btn = document.getElementById('toggleCamera');
        btn.textContent = enabled ? '📷' : '📵';
        btn.title = enabled ? 'Turn off camera' : 'Turn on camera';
    });

    document.getElementById('screenShareBtn')?.addEventListener('click', async () => {
        const sharing = await WebRTC.toggleScreenShare();
        const btn = document.getElementById('screenShareBtn');
        btn.textContent = sharing ? '🛑' : '🖥️';
        btn.title = sharing ? 'Stop sharing' : 'Share screen';
    });

    // Leave room - emit before navigating
    document.querySelector('.room-header a[href*="lobby"]')?.addEventListener('click', (e) => {
        e.preventDefault();
        socket.emit('leave_room', { room_code: roomCode });
        window.location.href = '/lobby';
    });

    // Emit leave when page is about to unload (close tab, refresh)
    window.addEventListener('beforeunload', () => {
        socket.emit('leave_room', { room_code: roomCode });
    });

    // Tab switching (Chat / Whiteboard)
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const panel = document.getElementById(tab === 'chat' ? 'chatPanel' : 'whiteboardPanel');
            if (panel) panel.classList.add('active');
        });
    });
})();
