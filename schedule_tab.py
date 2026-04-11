import json, os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDateTimeEdit, QFileDialog, QFrame, QMessageBox)
from PySide6.QtCore import QDateTime, Qt

class ScheduleTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.selected_sched_id = None
        self.embedded_json_content = ""
        self.setup_ui()

    def setup_ui(self):
        # MAIN LAYOUT
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)

        # --- STEP 1: FILE BINDING ---
        self.main_layout.addWidget(QLabel("<b>STEP 1: BIND QUIZ FILE</b>"))
        file_row = QHBoxLayout()
        self.file_display = QLineEdit()
        self.file_display.setPlaceholderText("No file selected...")
        self.file_display.setReadOnly(True)
        self.btn_browse = QPushButton("Browse JSON")
        self.btn_browse.clicked.connect(self.browse_quiz_file)
        file_row.addWidget(self.file_display)
        file_row.addWidget(self.btn_browse)
        self.main_layout.addLayout(file_row)

        # --- STEP 2: DETAILS ---
        self.main_layout.addWidget(QLabel("<b>STEP 2: SCHEDULE DETAILS</b>"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Quiz Title (e.g. Midterm Exam)")
        self.main_layout.addWidget(QLabel("Display Title:"))
        self.main_layout.addWidget(self.title_input)

        # --- DATE TIME PICKERS (THE FIX) ---
        # We create a horizontal layout specifically for the two pickers
        dt_container = QHBoxLayout()
        
        # Start Date
        v_start = QVBoxLayout()
        self.start_dt = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_dt.setCalendarPopup(True)
        self.start_dt.setDisplayFormat("yyyy-MM-dd HH:mm") # Ensure easy reading
        v_start.addWidget(QLabel("<b>Start Time:</b>"))
        v_start.addWidget(self.start_dt)
        
        # End Date
        v_end = QVBoxLayout()
        self.end_dt = QDateTimeEdit(QDateTime.currentDateTime().addDays(1))
        self.end_dt.setCalendarPopup(True)
        self.end_dt.setDisplayFormat("yyyy-MM-dd HH:mm")
        v_end.addWidget(QLabel("<b>End Time:</b>"))
        v_end.addWidget(self.end_dt)
        
        # Add the vertical columns to the horizontal row
        dt_container.addLayout(v_start)
        dt_container.addLayout(v_end)
        
        # Add the row to the main layout
        self.main_layout.addLayout(dt_container)

        # --- STEP 3: SAVE BUTTONS ---
        self.btn_save = QPushButton("Save Schedule")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_schedule)
        self.main_layout.addWidget(self.btn_save)

        self.main_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))

        # --- STEP 4: TABLE ---
        self.main_layout.addWidget(QLabel("<b>ACTIVE SCHEDULES</b>"))
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Start Time", "End Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemClicked.connect(self.load_schedule_data)
        self.main_layout.addWidget(self.table)

        self.btn_del = QPushButton("Delete Selected")
        self.btn_del.setStyleSheet("background-color: #e74c3c; color: white;")
        self.btn_del.clicked.connect(self.delete_schedule)
        self.main_layout.addWidget(self.btn_del)

        self.refresh_table()

    def browse_quiz_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Quiz", "", "JSON (*.json)")
        if path:
            with open(path, 'r') as f:
                self.embedded_json_content = json.dumps(json.load(f))
                self.file_display.setText(os.path.basename(path))

    def save_schedule(self):
        title = self.title_input.text().strip()
        # Format dates for SQLite comparison
        start = self.start_dt.dateTime().toString("yyyy-MM-dd HH:mm")
        end = self.end_dt.dateTime().toString("yyyy-MM-dd HH:mm")

        if not title or not self.embedded_json_content:
            QMessageBox.warning(self, "Error", "Title and Quiz File are required.")
            return

        if self.selected_sched_id:
            # UPDATE
            sql = """UPDATE schedules SET quiz_title=?, quiz_name=?, quiz_data=?, 
                    start_time=?, end_time=? WHERE id=?"""
            self.db.query(sql, (title, self.file_display.text(), self.embedded_json_content, 
                                start, end, self.selected_sched_id))
        else:
            # INSERT
            sql = """INSERT INTO schedules (quiz_title, quiz_name, quiz_data, start_time, end_time) 
                    VALUES (?,?,?,?,?)"""
            self.db.query(sql, (title, self.file_display.text(), self.embedded_json_content, start, end))

        self.refresh_table()
        self.clear_form()

    def load_schedule_data(self, item):
        """Loads data from the table back into the form for updating."""
        row = item.row()
        self.selected_sched_id = self.table.item(row, 0).text()
        
        # Fetch full data from DB (to get the embedded JSON and quiz name)
        res = self.db.query("SELECT * FROM schedules WHERE id=?", (self.selected_sched_id,)).fetchone()
        
        if res:
            # res indices match columns: id(0), title(1), quiz_name(2), quiz_data(3), code(4), start(5), end(6)
            self.title_input.setText(res[1])
            self.file_display.setText(res[2])
            self.embedded_json_content = res[3]
            self.start_dt.setDateTime(QDateTime.fromString(res[5], "yyyy-MM-dd HH:mm"))
            self.end_dt.setDateTime(QDateTime.fromString(res[6], "yyyy-MM-dd HH:mm"))
            
            # UI Feedback for Update Mode
            self.btn_save.setText("Update Selected Schedule")
            self.btn_save.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; height: 35px;")

    def delete_schedule(self):
        if self.selected_sched_id:
            self.db.query("DELETE FROM schedules WHERE id=?", (self.selected_sched_id,))
            self.refresh_table(); self.clear_form()

    def clear_form(self):
        self.selected_sched_id = None
        self.embedded_json_content = ""
        self.btn_save.setText("Save Schedule")
        self.btn_save.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; height: 35px;")

    def refresh_table(self):
        self.table.setRowCount(0)
        res = self.db.query("SELECT id, quiz_title, start_time, end_time FROM schedules")
        for r_idx, row in enumerate(res.fetchall()):
            self.table.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))