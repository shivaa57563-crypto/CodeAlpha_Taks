# Project Management Tool

A simple Trello/Asana-style project management web app built with **Flask**, **SQLite**, **HTML**, **CSS**, and **JavaScript**. Suitable for beginners and college projects.

## Features

- **User accounts**: Register and log in with sessions
- **Projects**: Create projects and join existing ones
- **Tasks**: Add tasks with title, description, assignee, and status (To Do, In Progress, Done)
- **Comments**: Comment on tasks
- **Dashboard**: View all your projects in one place
- **Responsive UI**: Clean, simple design that works on different screen sizes

## Project Structure

```
new project/
├── app.py              # Main Flask application and routes
├── database.py         # Database connection and schema
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── database/           # SQLite database file is stored here
├── templates/          # HTML templates (Jinja2)
└── static/
    ├── css/
    │   └── style.css   # Styles
    └── js/
        └── main.js     # Front-end JavaScript
```

## How to Run Locally

### 1. Prerequisites

- **Python 3.8 or higher** installed on your computer
- A terminal (Command Prompt, PowerShell, or terminal in your editor)

### 2. Create a Virtual Environment (Recommended)

```bash
# Navigate to the project folder
cd "c:\Users\ADMIN\OneDrive\Desktop\new project"

# Create virtual environment
python -m venv venv

# Activate it:
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\venv\Scripts\activate.bat
# On Mac/Linux:
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

You should see something like:

```
* Running on http://127.0.0.1:5000
```

### 5. Open in Browser

Open your browser and go to: **http://127.0.0.1:5000**

- **First time**: Click "Register" to create an account, then log in.
- **Dashboard**: After login you'll see your projects. Create a new project, then open it to add tasks and comments.

## Default Behavior

- The SQLite database is created automatically in the `database/` folder the first time you run the app.
- Sessions are stored in the browser; logging out clears the session.
- Passwords are hashed (not stored in plain text).

## Tips for Students

- Read the comments in `app.py` and `database.py` to understand the flow.
- Templates use Jinja2: `{{ variable }}` for output, `{% for %}`, `{% if %}` for logic.
- Static files (CSS/JS) are in `static/` and linked from the base template.

Enjoy building and extending your project!
