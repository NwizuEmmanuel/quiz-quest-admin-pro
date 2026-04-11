import csv
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDateTimeEdit, QFileDialog, QMessageBox)
from PySide6.QtCore import QDateTime

class ResultsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # --- FILTERS ---
        filter_layout = QHBoxLayout()
        self.start_filter = QDateTimeEdit(QDateTime.currentDateTime().addDays(-7))
        self.start_filter.setCalendarPopup(True)
        self.end_filter = QDateTimeEdit(QDateTime.currentDateTime().addDays(1))
        self.end_filter.setCalendarPopup(True)
        
        btn_refresh = QPushButton("Filter Results")
        btn_refresh.clicked.connect(self.load_results)
        btn_export = QPushButton("Export to CSV")
        btn_export.setStyleSheet("background-color: #27ae60; color: white;")
        btn_export.clicked.connect(self.export_csv)

        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.start_filter)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_filter)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addWidget(btn_export)
        layout.addLayout(filter_layout)

        # --- TABLE ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Student ID", "Quiz Title", "Score", "Total", "Percentage (%)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.load_results()

    def load_results(self):
        start = self.start_filter.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end = self.end_filter.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        
        query = """SELECT id, student_id, quiz_title, score, total 
                   FROM results WHERE timestamp BETWEEN ? AND ?"""
        rows = self.db.query(query, (start, end))

        self.table.setRowCount(0)
        for row_data in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            
            # Calculate Percentage
            score = row_data[3]
            total = row_data[4]
            percentage = (score / total * 100) if total > 0 else 0
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row_data[2]))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(score)))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(total)))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{percentage:.2f}%"))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "CSV Files (*.csv)")
        if not path: return

        try:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                # Header
                writer.writerow(["ID", "Student ID", "Quiz", "Score", "Total", "Percentage"])
                # Data
                for r in range(self.table.rowCount()):
                    row = [self.table.item(r, c).text() for c in range(self.table.columnCount())]
                    writer.writerow(row)
            QMessageBox.information(self, "Success", "Data exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")