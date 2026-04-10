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
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # --- 1. Quiz File Binding ---
        layout.addWidget(QLabel("<b>STEP 1: BIND QUIZ FILE</b>"))
        f_lay = QHBoxLayout()
        self.file_display = QLineEdit(); self.file_display.setReadOnly(True)
        self.file_display.setPlaceholderText("Select a quiz JSON to embed...")
        self.btn_browse = QPushButton("Browse JSON")
        self.btn_browse.clicked.connect(self.browse_quiz_file)
        f_lay.addWidget(self.file_display); f_lay.addWidget(self.btn_browse)
        layout.addLayout(f_lay)

        # --- 2. Details ---
        layout.addWidget(QLabel("<b>STEP 2: SCHEDULE DETAILS</b>"))
        self.title_input = QLineEdit(); self.title_input.setPlaceholderText("e.g., Midterm Exam")
        self.passcode_input = QLineEdit(); self.passcode_input.setPlaceholderText("e.g., 1234")
        
        layout.addWidget(QLabel("Display Title:")); layout.addWidget(self.title_input)
        layout.addWidget(QLabel("Passcode:")); layout.addWidget(self.passcode_input)

        # Dates
        dt_row = QHBoxLayout()
        self.start_dt = QDateTimeEdit(QDateTime.currentDateTime()); self.start_dt.setCalendarPopup(True)
        self.end_dt = QDateTimeEdit(QDateTime.currentDateTime().addDays(1)); self.end_dt.setCalendarPopup(True)
        
        v1 = QVBoxLayout(); v1.addWidget(QLabel("Start Time:")); v1.addWidget(self.start_dt)
        v2 = QVBoxLayout(); v2.addWidget(QLabel("End Time:")); v2.addWidget(self.end_dt)
        dt_row.addLayout(v1); dt_row.addLayout(v2)
        layout.addLayout(dt_row)

        # --- 3. CRUD Buttons ---
        self.btn_save = QPushButton("Save Schedule")
        self.btn_save.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; height: 35px;")
        self.btn_save.clicked.connect(self.save_schedule)
        
        self.btn_clear = QPushButton("Clear/Cancel")
        self.btn_clear.clicked.connect(self.clear_form)
        
        lay_btns = QHBoxLayout(); lay_btns.addWidget(self.btn_save); lay_btns.addWidget(self.btn_clear)
        layout.addLayout(lay_btns)

        layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))

        # --- 4. Table ---
        layout.addWidget(QLabel("<b>EXISTING SCHEDULES</b>"))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Quiz Title", "Passcode", "Start", "End"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemClicked.connect(self.load_schedule_data) # Click to load for update
        layout.addWidget(self.table)

        self.btn_del = QPushButton("Delete Selected")
        self.btn_del.setStyleSheet("background-color: #e74c3c; color: white;")
        self.btn_del.clicked.connect(self.delete_schedule)
        layout.addWidget(self.btn_del)

        self.refresh_table()

    def browse_quiz_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Quiz", "", "JSON (*.json)")
        if path:
            with open(path, 'r') as f:
                self.embedded_json_content = json.dumps(json.load(f))
                self.file_display.setText(os.path.basename(path))

    def save_schedule(self):
        """The heart of the Update feature."""
        title = self.title_input.text().strip()
        code = self.passcode_input.text().strip()
        start = self.start_dt.dateTime().toString("yyyy-MM-dd HH:mm")
        end = self.end_dt.dateTime().toString("yyyy-MM-dd HH:mm")

        if not title or not self.embedded_json_content:
            QMessageBox.warning(self, "Required", "Title and Quiz File are required.")
            return

        if self.selected_sched_id:
            # UPDATE MODE
            sql = """UPDATE schedules SET quiz_title=?, quiz_name=?, quiz_data=?, 
                     pass_code=?, start_time=?, end_time=? WHERE id=?"""
            self.db.query(sql, (title, self.file_display.text(), self.embedded_json_content, 
                                code, start, end, self.selected_sched_id))
            QMessageBox.information(self, "Updated", "Schedule successfully updated.")
        else:
            # CREATE MODE
            sql = """INSERT INTO schedules (quiz_title, quiz_name, quiz_data, pass_code, start_time, end_time) 
                     VALUES (?,?,?,?,?,?)"""
            self.db.query(sql, (title, self.file_display.text(), self.embedded_json_content, code, start, end))
            QMessageBox.information(self, "Saved", "New schedule created.")

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
            self.passcode_input.setText(res[4])
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
        self.title_input.clear(); self.file_display.clear(); self.passcode_input.clear()
        self.embedded_json_content = ""
        self.btn_save.setText("Save Schedule")
        self.btn_save.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; height: 35px;")

    def refresh_table(self):
        self.table.setRowCount(0)
        res = self.db.query("SELECT id, quiz_title, pass_code, start_time, end_time FROM schedules")
        for r_idx, row in enumerate(res.fetchall()):
            self.table.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))