/**
 * Chat module - Real-time text chat in the room.
 * Sends and receives messages via Socket.IO.
 */

const Chat = (function() {
    let socket = null;
    let roomCode = null;
    let username = null;

    /**
     * Initialize chat with socket and room info.
     */
    function init(sock, room, user) {
        socket = sock;
        roomCode = room;
        username = user;
        setupListeners();
        setupForm();
    }

    function setupListeners() {
        socket.on('chat_message', (data) => {
            addMessage(data.username, data.message, false);
        });
        socket.on('user_joined', (data) => {
            addSystemMessage(data.username + ' joined the room');
        });
        socket.on('user_left', () => {
            addSystemMessage('A user left the room');
        });
    }

    function setupForm() {
        const form = document.getElementById('chatForm');
        const input = document.getElementById('chatInput');
        if (form && input) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const msg = input.value.trim();
                if (msg && roomCode && username) {
                    socket.emit('chat_message', {
                        room_code: roomCode,
                        username: username,
                        message: msg
                    });
                    addMessage(username, msg, true);
                    input.value = '';
                }
            });
        }
    }

    /**
     * Add a message to the chat display.
     */
    function addMessage(user, text, isOwn) {
        const container = document.getElementById('chatMessages');
        if (!container) return;
        const div = document.createElement('div');
        div.className = 'chat-msg' + (isOwn ? ' own' : '');
        div.innerHTML = '<span class="chat-user">' + escapeHtml(user) + ':</span> ' + escapeHtml(text);
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    /**
     * Add a system message (join/leave notifications).
     */
    function addSystemMessage(text) {
        const container = document.getElementById('chatMessages');
        if (!container) return;
        const div = document.createElement('div');
        div.className = 'chat-msg system';
        div.textContent = text;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    return { init };
})();
