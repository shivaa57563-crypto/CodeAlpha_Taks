# Mini Social Media Web App

A beginner-friendly full-stack mini social media app built with **Python Flask**, **SQLite**, **HTML**, **CSS**, and **JavaScript**.

## How to Run Locally

1. **Open a terminal in this folder:** `social-media-project`
2. **Create a virtual environment (optional):**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1   # Windows PowerShell
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app:**
   ```bash
   python app.py
   ```
5. **Open in browser:** http://127.0.0.1:5000

The SQLite database `social_app.db` is created automatically in this folder on first run.

## Pages

- `/` — Redirects to login or dashboard
- `/login`, `/register` — Auth
- `/dashboard` — Feed + create post
- `/discover` — List users to follow
- `/profile/<user_id>` — User profile
- `/logout` — Log out
