import multiprocessing
import socket
import time
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QHBoxLayout, QMessageBox)
from PySide6.QtCore import QDateTime, Qt

# 1. MOVE THIS OUTSIDE THE CLASS
# This prevents Windows from trying to serialize the UI objects
def flask_process_target():
    try:
        from server_worker import app 
        # use_reloader=False is MANDATORY here
        app.run(host='0.0.0.0', port=7777, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Flask Error: {e}")

class ServerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.server_process = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.status_label = QLabel("Server Status: <b>OFFLINE</b>")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px;")
        layout.addWidget(self.status_label)

        self.ip_label = QLabel(f"Server IP: {self.get_local_ip()}")
        layout.addWidget(self.ip_label)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("background-color: #2c3e50; color: #ecf0f1; font-family: Consolas;")
        layout.addWidget(self.log_display)

        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("🚀 Start Server")
        self.btn_start.setFixedHeight(40)
        self.btn_start.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        self.btn_start.clicked.connect(self.start_server)
        
        self.btn_stop = QPushButton("🛑 Stop Server")
        self.btn_stop.setFixedHeight(40)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        self.btn_stop.clicked.connect(self.stop_server)
        
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        layout.addLayout(btn_layout)

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except: return "127.0.0.1"

    def start_server(self):
        # 2. Start the process using the top-level function
        self.server_process = multiprocessing.Process(target=flask_process_target)
        self.server_process.daemon = True 
        self.server_process.start()

        self.status_label.setText("Server Status: <b>RUNNING</b>")
        self.status_label.setStyleSheet("color: #2ecc71; font-size: 14px;")
        self.log_display.append(f"[{QDateTime.currentDateTime().toString('hh:mm:ss')}] Server started.")
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.join(timeout=1.0) # Wait a second for it to die
            if self.server_process.is_alive():
                self.server_process.kill() # Force kill if terminate failed
            self.server_process = None

        self.status_label.setText("Server Status: <b>OFFLINE</b>")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px;")
        self.log_display.append(f"[{QDateTime.currentDateTime().toString('hh:mm:ss')}] Server stopped.")
        
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)