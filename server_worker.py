import os
import json
import sqlite3
import threading
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Get the absolute path to the directory this script is in
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "quiz_system.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- API: Student Login Authentication ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    db = get_db()
    user = db.execute("SELECT id, firstname, lastname, section FROM students WHERE username=? AND password=?", 
                      (username, password)).fetchone()
    db.close()

    if user:
        return jsonify({
            "status": "success",
            "student_id": user['id'],
            "name": f"{user['firstname']} {user['lastname']}",
            "section": user['section']
        }), 200
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# --- API: Get Schedules (Filtered by current time) ---
@app.route('/api/get_schedules', methods=['GET'])
def get_schedules():
    db = get_db()
    # USE SECONDS: Matches the Admin App format exactly
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Checking for quizzes active at: {now}")

    query = """SELECT id, quiz_title, quiz_name FROM schedules 
               WHERE ? BETWEEN start_time AND end_time"""
    
    schedules = db.execute(query, (now,)).fetchall()
    db.close()
    return jsonify([dict(s) for s in schedules]), 200

# --- API: Get Full Quiz Data ---
@app.route('/api/get_full_quiz', methods=['POST'])
def get_full_quiz():
    data = request.json
    schedule_id = data.get('schedule_id')
    
    db = get_db()
    query = "SELECT quiz_title, quiz_data FROM schedules WHERE id=?"
    quiz = db.execute(query, (schedule_id,)).fetchone()
    db.close()
    
    if quiz:
        return jsonify({
            "title": quiz['quiz_title'],
            "questions": json.loads(quiz['quiz_data'])
        }), 200
    
    return jsonify({"status": "error", "message": "Quiz not found"}), 404

# --- API: Receive Quiz Results (Updated with Defeated Boss) ---
@app.route('/api/submit_results', methods=['POST'])
def submit_results():
    data = request.json
    db = get_db()
    
    # Store 'quiz_details' (the history) as a JSON string
    details_json = json.dumps(data.get('quiz_details', []))
    
    # NEW: Get defeated_boss from request, default to 'None' if missing
    boss = data.get('defeated_boss', 'None')
    
    # Updated query to include defeated_boss column
    query = """INSERT INTO results (student_id, quiz_title, score, total, defeated_boss, quiz_details) 
               VALUES (?, ?, ?, ?, ?, ?)"""
    
    try:
        db.execute(query, (
            data['student_id'], 
            data['quiz_title'], 
            data['score'], 
            data['total'], 
            boss,
            details_json
        ))
        db.commit()
        db.close()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        if db: db.close()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Server Thread Management ---
class ServerThread(threading.Thread):
    def __init__(self, host='0.0.0.0', port=7777): # Set host to 0.0.0.0 for LAN access
        super().__init__()
        self.host = host
        self.port = port
        self.daemon = True

    def run(self):
        # We run the app defined in this same file
        app.run(host=self.host, port=self.port, debug=False, use_reloader=False)