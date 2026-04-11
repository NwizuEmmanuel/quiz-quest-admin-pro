# 📝 Quiz Quest Architecture Pro

A full-stack, distributed quiz management system featuring a desktop **Admin Dashboard**, a **Flask REST API**, and a **Godot Game Engine** client. This system allows educators to create quizzes, manage students, schedule exams, and track real-time "Boss Battle" results.

## 🚀 System Architecture

1.  **Admin App (PySide6):** The control center for managing the SQLite database, student registration, and quiz scheduling.
2.  **Server (Flask):** A multi-processed backend that handles student authentication and data synchronization.
3.  **Client (Godot):** The student-facing game that fetches active quizzes and submits scores, including "Defeated Boss" data.

---

## 🛠️ Features

### **Admin Dashboard**
* **Student Management:** Full CRUD (Create, Read, Update, Delete) with real-time search and registration.
* **Quiz Scheduler:** Bind JSON quiz files to specific time windows using a calendar picker.
* **Advanced Analytics:** * Filter results by date range or student name.
    * **Defeated Boss Tracking:** See which game bosses students have conquered.
    * **Scrollable Breakdown:** Double-click any result to see a full question-by-question history.
    * **CSV Export:** Export filtered data for grading reports.
* **Server Control:** Start and stop the Flask backend directly from the UI using isolated processes.

### **Server API**
* **`POST /api/login`**: Authenticates students.
* **`GET /api/get_schedules`**: Returns quizzes active within the current time window.
* **`POST /api/get_full_quiz`**: Delivers the JSON question data for a specific schedule.
* **`POST /api/submit_results`**: Records scores, timestamps, boss data, and detailed answer history.

---

## 📂 Project Structure

```text
quiz-quest-admin/
├── main.py                # Application entry point
├── database.py            # SQLite wrapper (Row-factory enabled)
├── server_worker.py       # Flask API implementation
├── ui/
│   ├── student_tab.py     # Student registration logic
│   ├── schedule_tab.py    # Quiz timing & file binding
│   ├── results_tab.py     # Analytics & CSV export
│   └── server_tab.py      # Process-managed server control
└── quiz_system.db         # Unified SQLite database
```

---

## ⚙️ Installation

### 1. Requirements
* Python 3.10+
* `PySide6` (UI)
* `Flask` (Server)

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/your-repo/quiz-quest.git

# Install dependencies
pip install PySide6 Flask
```

### 3. Running the App
On Windows, ensure you run the main script. The system uses `multiprocessing.freeze_support()` to handle the server sub-process safely.
```bash
python main.py
```

---

## 🎮 Godot Integration

To connect your Godot game, use the `HTTPRequest` node to communicate with the Admin's IP address on port `7777`.

**Example Result Submission:**
```gdscript
var result_data = {
    "student_id": 1,
    "quiz_title": "Math 101",
    "score": 8,
    "total": 10,
    "defeated_boss": "Cyber-Dragon",
    "quiz_details": [
        {"question": "2+2?", "student_answer": "4", "status": "Correct"},
        {"question": "5+5?", "student_answer": "12", "status": "Incorrect"}
    ]
}
```

---

## 📊 Database Schema

The system automatically initializes `quiz_system.db` with the following tables:
* **`students`**: `id, firstname, lastname, section, username, password`
* **`schedules`**: `id, quiz_title, quiz_name, quiz_data (JSON), start_time, end_time`
* **`results`**: `id, student_id, quiz_title, score, total, defeated_boss, quiz_details (JSON), timestamp`

---

## ⚠️ Important Notes
* **Port:** The server defaults to port `7777`. Ensure your firewall allows incoming traffic on this port for student devices.
* **Time Sync:** Ensure the Admin PC and Student devices have synchronized clocks, as quiz availability is time-dependent.
* **JSON Format:** Quizzes must be valid JSON files containing an array of question objects.

---
*Built with ❤️ for Modern Educators.*