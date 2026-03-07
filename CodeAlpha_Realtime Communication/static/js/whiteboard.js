/**
 * Whiteboard module - Simple collaborative drawing using HTML canvas.
 * Syncs drawings across peers via Socket.IO.
 */

const Whiteboard = (function() {
    let canvas = null;
    let ctx = null;
    let socket = null;
    let roomCode = null;
    let isDrawing = false;
    let lastX = 0, lastY = 0;
    let currentColor = 'black';

    /**
     * Initialize whiteboard with socket and room info.
     */
    function init(sock, room) {
        socket = sock;
        roomCode = room;
        canvas = document.getElementById('whiteboard');
        if (!canvas) return;
        ctx = canvas.getContext('2d');
        ctx.strokeStyle = currentColor;
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';

        setupDrawing();
        setupToolbar();
        setupListeners();
    }

    function setupDrawing() {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        function getCoords(e) {
            const clientX = e.clientX !== undefined ? e.clientX : e.touches[0].clientX;
            const clientY = e.clientY !== undefined ? e.clientY : e.touches[0].clientY;
            return {
                x: (clientX - rect.left) * scaleX,
                y: (clientY - rect.top) * scaleY
            };
        }

        canvas.addEventListener('mousedown', (e) => {
            const coords = getCoords(e);
            isDrawing = true;
            lastX = coords.x;
            lastY = coords.y;
        });

        canvas.addEventListener('mousemove', (e) => {
            if (!isDrawing) return;
            const coords = getCoords(e);
            draw(lastX, lastY, coords.x, coords.y, currentColor);
            socket.emit('whiteboard_draw', {
                room_code: roomCode,
                x1: lastX, y1: lastY,
                x2: coords.x, y2: coords.y,
                color: currentColor
            });
            lastX = coords.x;
            lastY = coords.y;
        });

        canvas.addEventListener('mouseup', () => { isDrawing = false; });
        canvas.addEventListener('mouseleave', () => { isDrawing = false; });

        // Touch support for mobile
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const coords = getCoords(e);
            isDrawing = true;
            lastX = coords.x;
            lastY = coords.y;
        });
        canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (!isDrawing) return;
            const coords = getCoords(e);
            draw(lastX, lastY, coords.x, coords.y, currentColor);
            socket.emit('whiteboard_draw', {
                room_code: roomCode,
                x1: lastX, y1: lastY,
                x2: coords.x, y2: coords.y,
                color: currentColor
            });
            lastX = coords.x;
            lastY = coords.y;
        });
        canvas.addEventListener('touchend', () => { isDrawing = false; });
    }

    function setupToolbar() {
        document.querySelectorAll('.wb-btn[data-color]').forEach(btn => {
            btn.addEventListener('click', () => {
                currentColor = btn.dataset.color;
                ctx.strokeStyle = currentColor;
                document.querySelectorAll('.wb-btn[data-color]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
        const clearBtn = document.getElementById('wbClear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                socket.emit('whiteboard_clear', { room_code: roomCode });
            });
        }
    }

    function setupListeners() {
        socket.on('whiteboard_draw', (data) => {
            draw(data.x1, data.y1, data.x2, data.y2, data.color || 'black');
        });
        socket.on('whiteboard_clear', () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        });
    }

    /**
     * Draw a line segment.
     */
    function draw(x1, y1, x2, y2, color) {
        ctx.strokeStyle = color || currentColor;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
    }

    return { init };
})();
