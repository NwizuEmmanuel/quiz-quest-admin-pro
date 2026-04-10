from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFrame, QMessageBox)
from PySide6.QtCore import Qt

class StudentTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.selected_student_id = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # --- Search Section ---
        layout.addWidget(QLabel("<b>SEARCH STUDENTS</b>"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by First Name or Last Name...")
        self.search_input.textChanged.connect(self.filter_table)
        layout.addWidget(self.search_input)
        
        layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))

        # --- Input Section ---
        layout.addWidget(QLabel("<b>STUDENT REGISTRATION / UPDATE</b>"))
        
        # Grid-like layout for inputs
        self.f_name = QLineEdit(); self.f_name.setPlaceholderText("e.g. John")
        self.l_name = QLineEdit(); self.l_name.setPlaceholderText("e.g. Doe")
        self.section = QLineEdit(); self.section.setPlaceholderText("e.g. Grade 10 - Blue")
        self.user = QLineEdit(); self.user.setPlaceholderText("Username")
        self.pwd = QLineEdit(); self.pwd.setPlaceholderText("Password")
        self.pwd.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout = QVBoxLayout()
        for lbl, w in [("First Name:", self.f_name), ("Last Name:", self.l_name), 
                       ("Section:", self.section), ("Username:", self.user), ("Password:", self.pwd)]:
            form_layout.addWidget(QLabel(f"<b>{lbl}</b>"))
            form_layout.addWidget(w)
        layout.addLayout(form_layout)

        # Buttons
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save Student")
        self.save_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; height: 35px;")
        self.save_btn.clicked.connect(self.save_student)
        
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self.clear_form)
        
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.clear_btn)
        layout.addLayout(btn_row)

        layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))

        # --- Table Section ---
        layout.addWidget(QLabel("<b>REGISTERED STUDENTS LIST</b>"))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Section", "Username"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemClicked.connect(self.load_to_form)
        layout.addWidget(self.table)

        # Delete Action
        del_row = QHBoxLayout()
        self.del_btn = QPushButton("🗑️ Delete Selected Student")
        self.del_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        self.del_btn.clicked.connect(self.delete_student)
        del_row.addStretch()
        del_row.addWidget(self.del_btn)
        layout.addLayout(del_row)

        self.refresh_table()

    def save_student(self):
        """Handles both Creation and Updating."""
        f = self.f_name.text().strip()
        l = self.l_name.text().strip()
        s = self.section.text().strip()
        u = self.user.text().strip()
        p = self.pwd.text().strip()

        if not all([f, l, s, u, p]):
            QMessageBox.warning(self, "Required Fields", "All fields must be filled.")
            return

        if self.selected_student_id:
            # Update existing
            sql = "UPDATE students SET firstname=?, lastname=?, section=?, username=?, password=? WHERE id=?"
            self.db.query(sql, (f, l, s, u, p, self.selected_student_id))
            QMessageBox.information(self, "Updated", "Student record updated successfully.")
        else:
            # Insert new
            try:
                sql = "INSERT INTO students (firstname, lastname, section, username, password) VALUES (?,?,?,?,?)"
                self.db.query(sql, (f, l, s, u, p))
                QMessageBox.information(self, "Saved", "New student registered.")
            except:
                QMessageBox.critical(self, "Error", "Username might already exist.")
        
        self.refresh_table()
        self.clear_form()

    def load_to_form(self, item):
        """When a row is clicked, load the data back into the inputs for updating."""
        row = item.row()
        # Retrieve the ID from the first column
        self.selected_student_id = self.table.item(row, 0).text()
        
        # Re-query the DB to get the password (which isn't in the table)
        res = self.db.query("SELECT firstname, lastname, section, username, password FROM students WHERE id=?", 
                            (self.selected_student_id,)).fetchone()
        
        if res:
            self.f_name.setText(res[0])
            self.l_name.setText(res[1])
            self.section.setText(res[2])
            self.user.setText(res[3])
            self.pwd.setText(res[4])
            self.save_btn.setText("Update Student Information")
            self.save_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; height: 35px;")

    def filter_table(self):
        """Real-time search filter."""
        search_text = self.search_input.text().lower()
        for i in range(self.table.rowCount()):
            # Check First Name (Col 1) and Last Name (Col 2)
            first_name = self.table.item(i, 1).text().lower()
            last_name = self.table.item(i, 2).text().lower()
            
            if search_text in first_name or search_text in last_name:
                self.table.setRowHidden(i, False)
            else:
                self.table.setRowHidden(i, True)

    def delete_student(self):
        if not self.selected_student_id:
            QMessageBox.warning(self, "Select Student", "Please click on a student in the table first.")
            return

        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this student?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.db.query("DELETE FROM students WHERE id=?", (self.selected_student_id,))
            self.refresh_table()
            self.clear_form()

    def clear_form(self):
        self.selected_student_id = None
        self.f_name.clear()
        self.l_name.clear()
        self.section.clear()
        self.user.clear()
        self.pwd.clear()
        self.save_btn.setText("Save Student")
        self.save_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; height: 35px;")

    def refresh_table(self):
        self.table.setRowCount(0)
        res = self.db.query("SELECT id, firstname, lastname, section, username FROM students")
        for r_idx, row in enumerate(res.fetchall()):
            self.table.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable) # Make table read-only
                self.table.setItem(r_idx, c_idx, item)