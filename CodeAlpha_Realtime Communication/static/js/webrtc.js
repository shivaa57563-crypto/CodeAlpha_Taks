/**
 * WebRTC module - Peer-to-peer video/audio and screen sharing.
 * Handles local/remote streams, signaling, and media controls.
 */

const WebRTC = (function() {
    let localStream = null;
    let peerConnections = {};  // sid -> RTCPeerConnection
    let remoteStreams = {};    // sid -> MediaStream
    let socket = null;
    let roomCode = null;
    let username = null;
    let isScreenSharing = false;
    let screenStream = null;

    const iceServers = [
        { urls: 'stun:stun.l.google.com:19302' }
    ];

    /**
     * Initialize WebRTC with socket and room info.
     */
    function init(sock, room, user) {
        socket = sock;
        roomCode = room;
        username = user;
        setupLocalStream();
        setupSignaling();
    }

    /**
     * Get user media (camera + mic) for local video.
     */
    async function setupLocalStream() {
        try {
            localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            const video = document.getElementById('localVideo');
            if (video) video.srcObject = localStream;
        } catch (err) {
            console.error('Error getting media:', err);
            showError('Could not access camera/microphone. Please allow permissions.');
        }
    }

    /**
     * Create RTCPeerConnection for a peer.
     */
    function createPeerConnection(remoteSid) {
        const pc = new RTCPeerConnection({ iceServers });
        peerConnections[remoteSid] = pc;

        pc.onicecandidate = (e) => {
            if (e.candidate) {
                socket.emit('webrtc_ice_candidate', {
                    target_sid: remoteSid,
                    from_sid: socket.id,
                    candidate: e.candidate
                });
            }
        };

        pc.ontrack = (e) => {
            if (e.streams && e.streams[0]) {
                remoteStreams[remoteSid] = e.streams[0];
                addRemoteVideo(remoteSid, e.streams[0]);
            }
        };

        pc.onconnectionstatechange = () => {
            if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected') {
                removeRemoteVideo(remoteSid);
            }
        };

        if (localStream) {
            localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
        }
        return pc;
    }

    /**
     * Add remote video element to the grid.
     */
    function addRemoteVideo(sid, stream) {
        const container = document.getElementById('remoteVideos');
        const existing = document.getElementById('remote-' + sid);
        if (existing) return;

        const div = document.createElement('div');
        div.className = 'video-container remote';
        div.id = 'remote-' + sid;
        const video = document.createElement('video');
        video.autoplay = true;
        video.playsInline = true;
        video.srcObject = stream;
        const label = document.createElement('span');
        label.className = 'video-label';
        label.textContent = 'Remote';
        div.appendChild(video);
        div.appendChild(label);
        container.appendChild(div);
    }

    /**
     * Remove remote video when peer disconnects.
     */
    function removeRemoteVideo(sid) {
        const el = document.getElementById('remote-' + sid);
        if (el) el.remove();
        if (peerConnections[sid]) {
            peerConnections[sid].close();
            delete peerConnections[sid];
        }
        delete remoteStreams[sid];
    }

    /**
     * Create offer and send to remote peer.
     */
    async function createAndSendOffer(remoteSid) {
        const pc = createPeerConnection(remoteSid);
        try {
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);
            socket.emit('webrtc_offer', {
                target_sid: remoteSid,
                offer: offer,
                from_sid: socket.id
            });
        } catch (err) {
            console.error('Error creating offer:', err);
        }
    }

    /**
     * Handle incoming offer - create answer and send back.
     */
    async function handleOffer(data) {
        const { offer, from_sid } = data;
        const pc = createPeerConnection(from_sid);
        try {
            await pc.setRemoteDescription(new RTCSessionDescription(offer));
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);
            socket.emit('webrtc_answer', {
                target_sid: from_sid,
                answer: answer
            });
        } catch (err) {
            console.error('Error handling offer:', err);
        }
    }

    /**
     * Handle incoming answer.
     */
    async function handleAnswer(data) {
        const answer = data.answer;
        const fromSid = data.from_sid || data.target_sid;
        const pc = peerConnections[fromSid];
        if (pc) {
            await pc.setRemoteDescription(new RTCSessionDescription(answer));
        }
    }

    /**
     * Handle ICE candidate.
     */
    async function handleIceCandidate(data) {
        const { candidate } = data;
        const from_sid = data.from_sid || data.target_sid;
        const pc = peerConnections[from_sid];
        if (pc) {
            await pc.addIceCandidate(new RTCIceCandidate(candidate));
        }
    }

    /**
     * Setup socket listeners for WebRTC signaling.
     */
    function setupSignaling() {
        socket.on('room_joined', async (data) => {
            const peers = data.peers || [];
            for (const peer of peers) {
                await createAndSendOffer(peer.sid);
            }
        });

        socket.on('user_joined', async (data) => {
            await createAndSendOffer(data.sid);
        });

        socket.on('user_left', (data) => {
            removeRemoteVideo(data.sid);
        });

        socket.on('webrtc_offer', (data) => {
            const fromSid = data.from_sid || data.target_sid;
            handleOffer({ offer: data.offer, from_sid: fromSid });
        });

        socket.on('webrtc_answer', (data) => {
            handleAnswer({
                answer: data.answer,
                from_sid: data.from_sid,
                target_sid: data.target_sid
            });
        });

        socket.on('webrtc_ice_candidate', (data) => {
            handleIceCandidate({
                candidate: data.candidate,
                from_sid: data.from_sid,
                target_sid: data.target_sid
            });
        });
    }

    function showError(msg) {
        const grid = document.getElementById('videoGrid');
        if (grid) {
            const err = document.createElement('div');
            err.className = 'video-error';
            err.textContent = msg;
            grid.appendChild(err);
        }
    }

    /**
     * Toggle microphone mute.
     */
    function toggleMic() {
        if (!localStream) return;
        const audioTrack = localStream.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = !audioTrack.enabled;
            return audioTrack.enabled;
        }
        return false;
    }

    /**
     * Toggle camera on/off.
     */
    function toggleCamera() {
        if (!localStream) return;
        const videoTrack = localStream.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.enabled = !videoTrack.enabled;
            return videoTrack.enabled;
        }
        return false;
    }

    /**
     * Toggle screen sharing.
     */
    async function toggleScreenShare() {
        try {
            if (isScreenSharing) {
                if (screenStream) {
                    screenStream.getTracks().forEach(t => t.stop());
                    screenStream = null;
                }
                const videoTrack = localStream.getVideoTracks()[0];
                if (videoTrack) videoTrack.enabled = true;
                Object.values(peerConnections).forEach(pc => {
                    const senders = pc.getSenders();
                    const videoSender = senders.find(s => s.track && s.track.kind === 'video');
                    if (videoSender && localStream) {
                        const track = localStream.getVideoTracks()[0];
                        if (track) videoSender.replaceTrack(track);
                    }
                });
                document.getElementById('localVideo').srcObject = localStream;
                isScreenSharing = false;
                return false;
            } else {
                screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                const screenTrack = screenStream.getVideoTracks()[0];
                screenTrack.onended = () => toggleScreenShare();
                Object.values(peerConnections).forEach(pc => {
                    const senders = pc.getSenders();
                    const videoSender = senders.find(s => s.track && s.track.kind === 'video');
                    if (videoSender) videoSender.replaceTrack(screenTrack);
                });
                const newStream = new MediaStream([screenTrack, localStream.getAudioTracks()[0]].filter(Boolean));
                document.getElementById('localVideo').srcObject = newStream;
                isScreenSharing = true;
                return true;
            }
        } catch (err) {
            console.error('Screen share error:', err);
            showError('Screen sharing failed. Please try again.');
            return false;
        }
    }

    return {
        init,
        toggleMic,
        toggleCamera,
        toggleScreenShare
    };
})();
