# database.py
# Handles SQLite connection and table creation for the Project Management Tool.
# Keeps all database logic in one place for clarity.

import sqlite3
import os
from werkzeug.security import generate_password_hash

# Path to the database file inside the database folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "project_tool.db")


def get_db_connection():
    """
    Returns a connection to the SQLite database.
    Row factory is set so we get dict-like rows (access by column name).
    """
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # so we can use row["column_name"]
    return conn


def init_db():
    """
    Creates all tables if they don't exist.
    Call this when the app starts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users: store username and hashed password
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Projects: each project has a name and an owner (created_by)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # Project members: which users belong to which project (for "join" and permissions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(project_id, user_id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Tasks: belong to a project, have title, description, assignee, status
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            assigned_user_id INTEGER,
            status TEXT NOT NULL DEFAULT 'To Do',
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (assigned_user_id) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # Comments: attached to a task, written by a user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def add_user_as_project_member(conn, project_id, user_id):
    """
    Adds a user to a project's members (e.g. when they create the project).
    Ignores if already a member (UNIQUE constraint).
    """
    try:
        conn.execute(
            "INSERT INTO project_members (project_id, user_id) VALUES (?, ?)",
            (project_id, user_id)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()  # already a member
