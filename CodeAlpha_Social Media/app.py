"""
Mini Social Media App - Main Flask Application
A simple full-stack app with users, posts, comments, likes, and followers.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from database.init_db import get_connection, init_database, DB_PATH

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Ensure database exists when app starts
if not os.path.exists(DB_PATH):
    init_database()


def get_current_user():
    """Get the logged-in user from session, or None."""
    if 'user_id' not in session:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (session['user_id'],))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'id': row['id'], 'username': row['username'], 'email': row['email']}
    return None


def login_required(f):
    """Decorator: redirect to login if user is not logged in."""
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if get_current_user() is None:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped


# -------- AUTH ROUTES --------

@app.route('/')
def index():
    """Home: redirect to dashboard if logged in, else to login."""
    if get_current_user():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Show login form or process login."""
    if get_current_user():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html', user=None)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row and check_password_hash(row['password_hash'], password):
            session['user_id'] = row['id']
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html', user=None)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Show registration form or create new user."""
    if get_current_user():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        # Basic validation
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html', user=None)
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html', user=None)
        if len(password) < 4:
            flash('Password must be at least 4 characters.', 'error')
            return render_template('register.html', user=None)
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                flash('Username or email already taken.', 'error')
                conn.close()
                return render_template('register.html', user=None)
            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            session['user_id'] = cursor.lastrowid
            conn.close()
            flash('Account created! Welcome.', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            conn.rollback()
            conn.close()
            flash('Something went wrong. Try again.', 'error')
            return render_template('register.html', user=None)
    return render_template('register.html', user=None)


@app.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# -------- DASHBOARD (FEED) --------

@app.route('/dashboard')
@login_required
def dashboard():
    """Show the main feed: posts from users that the current user follows, plus own posts."""
    user = get_current_user()
    conn = get_connection()
    cursor = conn.cursor()
    # Get IDs of people we follow + ourselves
    cursor.execute(
        "SELECT following_id FROM followers WHERE follower_id = ?",
        (user['id'],)
    )
    following_ids = [r['following_id'] for r in cursor.fetchall()]
    following_ids.append(user['id'])
    if not following_ids:
        placeholders = '?'
    else:
        placeholders = ','.join('?' * len(following_ids))
    cursor.execute(
        f"SELECT p.id, p.content, p.created_at, p.user_id, u.username "
        f"FROM posts p JOIN users u ON p.user_id = u.id "
        f"WHERE p.user_id IN ({placeholders}) ORDER BY p.created_at DESC",
        tuple(following_ids)
    )
    posts = [dict(row) for row in cursor.fetchall()]
    # For each post, get comment count and like count and whether current user liked
    for post in posts:
        cursor.execute("SELECT COUNT(*) as c FROM comments WHERE post_id = ?", (post['id'],))
        post['comment_count'] = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(*) as c FROM likes WHERE post_id = ?", (post['id'],))
        post['like_count'] = cursor.fetchone()['c']
        cursor.execute("SELECT id FROM likes WHERE post_id = ? AND user_id = ?", (post['id'], user['id']))
        post['user_liked'] = cursor.fetchone() is not None
        # Load comments for this post (username + content + time)
        cursor.execute(
            "SELECT c.content, c.created_at, u.username FROM comments c "
            "JOIN users u ON c.user_id = u.id WHERE c.post_id = ? ORDER BY c.created_at",
            (post['id'],)
        )
        post['comments'] = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return render_template('dashboard.html', user=user, posts=posts)


@app.route('/post', methods=['POST'])
@login_required
def create_post():
    """Create a new post from the dashboard form."""
    content = request.form.get('content', '').strip()
    if not content:
        flash('Post cannot be empty.', 'error')
        return redirect(url_for('dashboard'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)", (get_current_user()['id'], content))
    conn.commit()
    conn.close()
    flash('Post created!', 'success')
    return redirect(url_for('dashboard'))


# -------- COMMENTS --------

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add a comment to a post. Redirect back to dashboard."""
    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('dashboard'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
    if not cursor.fetchone():
        conn.close()
        flash('Post not found.', 'error')
        return redirect(url_for('dashboard'))
    cursor.execute(
        "INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
        (post_id, get_current_user()['id'], content)
    )
    conn.commit()
    conn.close()
    flash('Comment added!', 'success')
    return redirect(url_for('dashboard'))


# -------- LIKES --------

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def toggle_like(post_id):
    """Like or unlike a post. Redirect back to dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
    if not cursor.fetchone():
        conn.close()
        flash('Post not found.', 'error')
        return redirect(url_for('dashboard'))
    cursor.execute("SELECT id FROM likes WHERE post_id = ? AND user_id = ?", (post_id, get_current_user()['id']))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("DELETE FROM likes WHERE post_id = ? AND user_id = ?", (post_id, get_current_user()['id']))
        flash('Like removed.', 'success')
    else:
        cursor.execute("INSERT INTO likes (post_id, user_id) VALUES (?, ?)", (post_id, get_current_user()['id']))
        flash('Liked!', 'success')
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


# -------- FOLLOW --------

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    """Follow or unfollow a user. Redirect back to that user's profile."""
    current_id = get_current_user()['id']
    if current_id == user_id:
        flash('You cannot follow yourself.', 'error')
        return redirect(url_for('profile', user_id=user_id))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        flash('User not found.', 'error')
        return redirect(url_for('dashboard'))
    cursor.execute("SELECT id FROM followers WHERE follower_id = ? AND following_id = ?", (current_id, user_id))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("DELETE FROM followers WHERE follower_id = ? AND following_id = ?", (current_id, user_id))
        flash('Unfollowed.', 'success')
    else:
        cursor.execute("INSERT INTO followers (follower_id, following_id) VALUES (?, ?)", (current_id, user_id))
        flash('Now following!', 'success')
    conn.commit()
    conn.close()
    return redirect(url_for('profile', user_id=user_id))


# -------- DISCOVER USERS --------

@app.route('/discover')
@login_required
def discover():
    """List all users so you can visit profiles and follow them."""
    user = get_current_user()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id != ? ORDER BY username", (user['id'],))
    users = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return render_template('discover.html', user=user, users=users)


# -------- PROFILE --------

@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    """Show a user's profile: their posts and follow button."""
    current_user = get_current_user()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        flash('User not found.', 'error')
        return redirect(url_for('dashboard'))
    profile_user = {'id': row['id'], 'username': row['username'], 'email': row['email']}
    # Get their posts
    cursor.execute(
        "SELECT p.id, p.content, p.created_at, p.user_id, u.username FROM posts p "
        "JOIN users u ON p.user_id = u.id WHERE p.user_id = ? ORDER BY p.created_at DESC",
        (user_id,)
    )
    posts = [dict(r) for r in cursor.fetchall()]
    for post in posts:
        cursor.execute("SELECT COUNT(*) as c FROM comments WHERE post_id = ?", (post['id'],))
        post['comment_count'] = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(*) as c FROM likes WHERE post_id = ?", (post['id'],))
        post['like_count'] = cursor.fetchone()['c']
        cursor.execute("SELECT id FROM likes WHERE post_id = ? AND user_id = ?", (post['id'], current_user['id']))
        post['user_liked'] = cursor.fetchone() is not None
        cursor.execute(
            "SELECT c.content, c.created_at, u.username FROM comments c "
            "JOIN users u ON c.user_id = u.id WHERE c.post_id = ? ORDER BY c.created_at",
            (post['id'],)
        )
        post['comments'] = [dict(r) for r in cursor.fetchall()]
    # Follower / following counts
    cursor.execute("SELECT COUNT(*) as c FROM followers WHERE following_id = ?", (user_id,))
    profile_user['follower_count'] = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM followers WHERE follower_id = ?", (user_id,))
    profile_user['following_count'] = cursor.fetchone()['c']
    # Is current user following this profile?
    cursor.execute(
        "SELECT id FROM followers WHERE follower_id = ? AND following_id = ?",
        (current_user['id'], user_id)
    )
    profile_user['is_following'] = cursor.fetchone() is not None
    conn.close()
    return render_template('profile.html', user=current_user, profile_user=profile_user, posts=posts)


# -------- RUN --------

if __name__ == '__main__':
    app.run(debug=True, port=5000)
