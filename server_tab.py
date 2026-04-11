from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFrame
from PySide6.QtCore import Qt
from server_worker import ServerThread

class ServerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.server_thread = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # --- Status Display ---
        layout.addWidget(QLabel("<b>SYSTEM SERVER STATUS</b>"))
        self.status_label = QLabel("🔴 OFFLINE")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 16px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))

        # --- Network Config (Locked) ---
        layout.addWidget(QLabel("<b>FIXED API CONFIGURATION</b>"))
        
        # Localhost IP
        self.ip_input = QLineEdit("127.0.0.1")
        self.ip_input.setReadOnly(True)
        self.ip_input.setStyleSheet("background-color: #ecf0f1; color: #7f8c8d; font-weight: bold;")
        
        # Game Port 7777
        self.port_input = QLineEdit("7777")
        self.port_input.setReadOnly(True)
        self.port_input.setStyleSheet("background-color: #ecf0f1; color: #7f8c8d; font-weight: bold;")
        
        layout.addWidget(QLabel("Server Address (Localhost):"))
        layout.addWidget(self.ip_input)
        layout.addWidget(QLabel("Communication Port (Game Standard):"))
        layout.addWidget(self.port_input)

        # --- Control Button ---
        self.btn_toggle = QPushButton("START SERVER")
        self.btn_toggle.setFixedHeight(50)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; 
                color: white; 
                font-weight: bold; 
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.btn_toggle.clicked.connect(self.start_server)
        layout.addWidget(self.btn_toggle)

        # Information Note
        note = QLabel("Note: The server uses the local loopback address for internal testing and security.")
        note.setWordWrap(True)
        note.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(note)

        layout.addStretch()

    def start_server(self):
        if not self.server_thread or not self.server_thread.is_alive():
            host = "127.0.0.1"
            port = 7777
            
            try:
                self.server_thread = ServerThread(host, port)
                self.server_thread.start()
                
                self.status_label.setText(f"🟢 ONLINE AT {host}:{port}")
                self.status_label.setStyleSheet("color: #27ae60; font-size: 16px; font-weight: bold;")
                self.btn_toggle.setText("SERVER RUNNING")
                self.btn_toggle.setEnabled(False) # Port is now occupied
            except Exception as e:
                self.status_label.setText("🔴 FAILED TO START")
                print(f"Server Error: {e}")