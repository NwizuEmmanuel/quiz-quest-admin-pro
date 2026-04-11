from flask import Flask, request, jsonify
import sqlite3
import threading

app = Flask(__name__)
DB_PATH = "school_data.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# API: Student Login Authentication
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

import json

from datetime import datetime

# API: Get Schedules (Filtered by current time)
@app.route('/api/get_schedules', methods=['GET'])
def get_schedules():
    db = get_db()
    # Get current server time in the same format as the Admin App
    now = datetime.now().strftime("%Y-%m-%d %H:mm")
    
    # Select only quizzes where 'now' is between start and end
    query = """SELECT id, quiz_title, quiz_name, start_time, end_time 
               FROM schedules WHERE ? BETWEEN start_time AND end_time"""
    schedules = db.execute(query, (now,)).fetchall()
    db.close()
    
    return jsonify([dict(s) for s in schedules]), 200

@app.route('/api/get_full_quiz', methods=['POST'])
def get_full_quiz():
    data = request.json
    schedule_id = data.get('schedule_id')
    
    db = get_db()
    # Ensure quiz_title is selected
    query = "SELECT quiz_title, quiz_data FROM schedules WHERE id=?"
    quiz = db.execute(query, (schedule_id,)).fetchone()
    db.close()
    
    if quiz:
        return jsonify({
            "title": quiz['quiz_title'], # This creates the 'title' key
            "questions": json.loads(quiz['quiz_data'])
        }), 200
    
    return jsonify({"status": "error", "message": "Quiz not found"}), 404

# API: Receive Quiz Results
@app.route('/api/submit_results', methods=['POST'])
def submit_results():
    data = request.json
    db = get_db()
    # Add quiz_details to your INSERT query
    db.execute("INSERT INTO results (student_id, quiz_title, score, total, quiz_details) VALUES (?,?,?,?,?)",
               (data['student_id'], data['quiz_title'], data['score'], data['total'], json.dumps(data.get('details'))))
    db.commit()
    return jsonify({"status": "success"}), 201

# Ensure this class in server_worker.py matches the call
class ServerThread(threading.Thread):
    def __init__(self, host='127.0.0.1', port=7777):
        super().__init__()
        self.host = host
        self.port = port
        self.daemon = True

    def run(self):
        # We use app.run directly. Threading handles the non-blocking part.
        from server_worker import app 
        app.run(host=self.host, port=self.port, debug=False, use_reloader=False)