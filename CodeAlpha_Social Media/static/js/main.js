// Basic JavaScript for the social media app
// Used for simple interactions like confirming actions

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    var messages = document.querySelectorAll('.message');
    messages.forEach(function(msg) {
        setTimeout(function() {
            msg.style.opacity = '0';
            msg.style.transition = 'opacity 0.5s';
            setTimeout(function() { msg.remove(); }, 500);
        }, 5000);
    });
});
