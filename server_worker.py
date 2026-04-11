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

# API: Receive Quiz Results
@app.route('/api/submit_results', methods=['POST'])
def submit_results():
    data = request.json # Expecting student_id, quiz_title, score, total
    db = get_db()
    try:
        db.execute("""INSERT INTO results (student_id, quiz_title, score, total, date_taken) 
                      VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""", 
                   (data['student_id'], data['quiz_title'], data['score'], data['total']))
        db.commit()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    finally:
        db.close()

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