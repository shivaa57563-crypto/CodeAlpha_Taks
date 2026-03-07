# app.py
# Main Flask application for the Project Management Tool.
# Handles: user auth, projects, tasks, and comments.

import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db_connection, init_db, add_user_as_project_member

app = Flask(__name__)
# Secret key for sessions - in a real app you'd use an env variable
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Valid task statuses (used for validation and display)
TASK_STATUSES = ["To Do", "In Progress", "Done"]


def login_required(f):
    """
    Decorator: redirects to login page if user is not in session.
    Use on any route that requires the user to be logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Please log in to continue.", "info")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Returns the current user dict from DB, or None if not logged in."""
    if session.get("user_id") is None:
        return None
    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, username FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    conn.close()
    return dict(user) if user else None


# ---------- Auth routes ----------

@app.route("/")
def index():
    """Home: redirect to dashboard if logged in, else to login."""
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration: form on GET, create user on POST."""
    if request.method == "GET":
        return render_template("register.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    confirm = request.form.get("confirm_password") or ""

    # Basic validation
    if not username:
        flash("Username is required.", "error")
        return render_template("register.html", username=username)
    if len(username) < 2:
        flash("Username must be at least 2 characters.", "error")
        return render_template("register.html", username=username)
    if not password:
        flash("Password is required.", "error")
        return render_template("register.html", username=username)
    if len(password) < 4:
        flash("Password must be at least 4 characters.", "error")
        return render_template("register.html", username=username)
    if password != confirm:
        flash("Passwords do not match.", "error")
        return render_template("register.html", username=username)

    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password))
        )
        conn.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
    except sqlite3.IntegrityError:
        conn.rollback()
        flash("That username is already taken.", "error")
        return render_template("register.html", username=username)
    finally:
        conn.close()


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login: form on GET, check credentials and set session on POST."""
    if request.method == "GET":
        return render_template("login.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    if not username or not password:
        flash("Username and password are required.", "error")
        return render_template("login.html", username=username)

    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        flash("Invalid username or password.", "error")
        return render_template("login.html", username=username)

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    flash("Welcome back!", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------- Dashboard (projects list) ----------

@app.route("/dashboard")
@login_required
def dashboard():
    """
    Show all projects the current user is a member of.
    Includes projects they created and ones they joined.
    """
    conn = get_db_connection()
    projects = conn.execute("""
        SELECT p.id, p.name, p.description, p.created_at,
               u.username AS owner_name
        FROM projects p
        JOIN project_members pm ON pm.project_id = p.id
        JOIN users u ON u.id = p.created_by
        WHERE pm.user_id = ?
        ORDER BY p.created_at DESC
    """, (session["user_id"],)).fetchall()
    conn.close()

    project_list = [dict(row) for row in projects]
    return render_template(
        "dashboard.html",
        projects=project_list,
        user=get_current_user()
    )


# ---------- Create project ----------

@app.route("/project/create", methods=["GET", "POST"])
@login_required
def create_project():
    """Create a new project. Creator is automatically added as a member."""
    if request.method == "GET":
        return render_template("create_project.html", user=get_current_user())

    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()

    if not name:
        flash("Project name is required.", "error")
        return render_template(
            "create_project.html",
            user=get_current_user(),
            name=name,
            description=description
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO projects (name, description, created_by) VALUES (?, ?, ?)",
        (name, description, session["user_id"])
    )
    project_id = cursor.lastrowid
    add_user_as_project_member(conn, project_id, session["user_id"])
    conn.close()

    flash("Project created successfully.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


# ---------- Join project (simple: by project ID) ----------

@app.route("/project/join", methods=["GET", "POST"])
@login_required
def join_project():
    """
    Join a project by entering its ID (e.g. from a link or shared by someone).
    In a student project we keep it simple: no invite codes.
    """
    if request.method == "GET":
        return render_template("join_project.html", user=get_current_user())

    project_id_raw = request.form.get("project_id") or ""
    try:
        project_id = int(project_id_raw)
    except ValueError:
        flash("Please enter a valid project ID (number).", "error")
        return render_template("join_project.html", user=get_current_user())

    conn = get_db_connection()
    project = conn.execute(
        "SELECT id, name FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    if not project:
        conn.close()
        flash("No project found with that ID.", "error")
        return render_template("join_project.html", user=get_current_user())

    add_user_as_project_member(conn, project_id, session["user_id"])
    conn.close()

    flash(f"You joined project: {project['name']}", "success")
    return redirect(url_for("project_detail", project_id=project_id))


# ---------- Project detail: tasks grouped by status ----------

def is_project_member(conn, project_id, user_id):
    """Check if user is a member of the project."""
    row = conn.execute(
        "SELECT 1 FROM project_members WHERE project_id = ? AND user_id = ?",
        (project_id, user_id)
    ).fetchone()
    return row is not None


@app.route("/project/<int:project_id>")
@login_required
def project_detail(project_id):
    """
    Show one project with its tasks grouped by status (To Do, In Progress, Done).
    Only allowed for project members.
    """
    conn = get_db_connection()
    project = conn.execute(
        "SELECT id, name, description, created_by FROM projects WHERE id = ?",
        (project_id,)
    ).fetchone()
    if not project:
        conn.close()
        flash("Project not found.", "error")
        return redirect(url_for("dashboard"))

    if not is_project_member(conn, project_id, session["user_id"]):
        conn.close()
        flash("You are not a member of this project.", "error")
        return redirect(url_for("dashboard"))

    # Get all tasks for this project with assignee username
    tasks = conn.execute("""
        SELECT t.id, t.title, t.description, t.assigned_user_id, t.status,
               t.created_at, u.username AS assignee_name
        FROM tasks t
        LEFT JOIN users u ON u.id = t.assigned_user_id
        WHERE t.project_id = ?
        ORDER BY t.created_at DESC
    """, (project_id,)).fetchall()

    # Get all members for the assignee dropdown
    members = conn.execute("""
        SELECT u.id, u.username
        FROM project_members pm
        JOIN users u ON u.id = pm.user_id
        WHERE pm.project_id = ?
        ORDER BY u.username
    """, (project_id,)).fetchall()

    conn.close()

    # Group tasks by status for the Kanban-style columns
    tasks_by_status = {status: [] for status in TASK_STATUSES}
    for row in tasks:
        task_dict = dict(row)
        tasks_by_status[task_dict["status"]].append(task_dict)

    return render_template(
        "project.html",
        project=dict(project),
        tasks_by_status=tasks_by_status,
        members=[dict(m) for m in members],
        statuses=TASK_STATUSES,
        user=get_current_user()
    )


# ---------- Create task ----------

@app.route("/project/<int:project_id>/task/create", methods=["POST"])
@login_required
def create_task(project_id):
    """Create a new task in the project. Only project members can create."""
    conn = get_db_connection()
    if not is_project_member(conn, project_id, session["user_id"]):
        conn.close()
        flash("You are not a member of this project.", "error")
        return redirect(url_for("dashboard"))

    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    assigned_user_id = request.form.get("assigned_user_id")
    status = request.form.get("status") or "To Do"

    if status not in TASK_STATUSES:
        status = "To Do"

    if not title:
        conn.close()
        flash("Task title is required.", "error")
        return redirect(url_for("project_detail", project_id=project_id))

    aid = None
    if assigned_user_id:
        try:
            aid = int(assigned_user_id)
        except ValueError:
            pass

    conn.execute("""
        INSERT INTO tasks (project_id, title, description, assigned_user_id, status, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (project_id, title, description, aid, status, session["user_id"]))
    conn.commit()
    conn.close()

    flash("Task created.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


# ---------- Update task status ----------

@app.route("/project/<int:project_id>/task/<int:task_id>/status", methods=["POST"])
@login_required
def update_task_status(project_id, task_id):
    """Update only the status of a task (e.g. move between columns)."""
    new_status = (request.form.get("status") or "").strip()
    if new_status not in TASK_STATUSES:
        flash("Invalid status.", "error")
        return redirect(url_for("project_detail", project_id=project_id))

    conn = get_db_connection()
    if not is_project_member(conn, project_id, session["user_id"]):
        conn.close()
        flash("You are not a member of this project.", "error")
        return redirect(url_for("dashboard"))

    conn.execute(
        "UPDATE tasks SET status = ? WHERE id = ? AND project_id = ?",
        (new_status, task_id, project_id)
    )
    conn.commit()
    conn.close()

    flash("Task status updated.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


# ---------- Task detail: view and comments ----------

@app.route("/project/<int:project_id>/task/<int:task_id>")
@login_required
def task_detail(project_id, task_id):
    """Show a single task with its comments. Only project members can view."""
    conn = get_db_connection()
    if not is_project_member(conn, project_id, session["user_id"]):
        conn.close()
        flash("You are not a member of this project.", "error")
        return redirect(url_for("dashboard"))

    task = conn.execute("""
        SELECT t.id, t.title, t.description, t.assigned_user_id, t.status, t.created_at,
               u.username AS assignee_name
        FROM tasks t
        LEFT JOIN users u ON u.id = t.assigned_user_id
        WHERE t.id = ? AND t.project_id = ?
    """, (task_id, project_id)).fetchone()
    if not task:
        conn.close()
        flash("Task not found.", "error")
        return redirect(url_for("project_detail", project_id=project_id))

    comments = conn.execute("""
        SELECT c.id, c.content, c.created_at, u.username
        FROM comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.task_id = ?
        ORDER BY c.created_at ASC
    """, (task_id,)).fetchall()

    project = conn.execute(
        "SELECT id, name FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    conn.close()

    return render_template(
        "task_detail.html",
        project=dict(project),
        task=dict(task),
        comments=[dict(c) for c in comments],
        statuses=TASK_STATUSES,
        user=get_current_user()
    )


# ---------- Add comment ----------

@app.route("/project/<int:project_id>/task/<int:task_id>/comment", methods=["POST"])
@login_required
def add_comment(project_id, task_id):
    """Add a comment to a task. Only project members can comment."""
    conn = get_db_connection()
    if not is_project_member(conn, project_id, session["user_id"]):
        conn.close()
        flash("You are not a member of this project.", "error")
        return redirect(url_for("dashboard"))

    # Check task exists and belongs to project
    task = conn.execute(
        "SELECT id FROM tasks WHERE id = ? AND project_id = ?",
        (task_id, project_id)
    ).fetchone()
    if not task:
        conn.close()
        flash("Task not found.", "error")
        return redirect(url_for("project_detail", project_id=project_id))

    content = (request.form.get("content") or "").strip()
    if not content:
        conn.close()
        flash("Comment cannot be empty.", "error")
        return redirect(url_for("task_detail", project_id=project_id, task_id=task_id))

    conn.execute(
        "INSERT INTO comments (task_id, user_id, content) VALUES (?, ?, ?)",
        (task_id, session["user_id"], content)
    )
    conn.commit()
    conn.close()

    flash("Comment added.", "success")
    return redirect(url_for("task_detail", project_id=project_id, task_id=task_id))


# ---------- Run the app ----------

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
