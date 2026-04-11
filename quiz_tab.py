import json
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QStackedWidget, 
                             QTextEdit, QListWidget, QFileDialog, QFrame, QMessageBox,
                             QSpinBox) # Added QSpinBox
from PySide6.QtCore import Signal

class QuizTab(QWidget):
    changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self.quiz_bank: list[dict[str, object]] = []
        self.editing_index = -1
        self.has_unsaved_changes = False
        self.current_file_path = None 
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        # --- Section: Question Content ---
        layout.addWidget(QLabel("<b>QUESTION PROMPT</b>"))
        self.q_input = QTextEdit()
        self.q_input.setPlaceholderText("Enter question...")
        self.q_input.setMaximumHeight(70)
        self.q_input.textChanged.connect(self.set_modified)
        layout.addWidget(self.q_input)

        # --- Section: Type & Time Limit (Added Time Limit here) ---
        type_time_layout = QHBoxLayout()
        
        v_type = QVBoxLayout()
        v_type.addWidget(QLabel("<b>TYPE</b>"))
        self.type_sel = QComboBox()
        self.type_sel.addItems(["Multiple Choice", "Identification"])
        self.type_sel.currentIndexChanged.connect(self.on_type_switch)
        v_type.addWidget(self.type_sel)
        
        v_time = QVBoxLayout()
        v_time.addWidget(QLabel("<b>TIME LIMIT (SEC)</b>"))
        self.time_limit = QSpinBox()
        self.time_limit.setRange(5, 600) # 5 seconds to 10 minutes
        self.time_limit.setValue(30)
        self.time_limit.valueChanged.connect(self.set_modified)
        v_time.addWidget(self.time_limit)
        
        type_time_layout.addLayout(v_type, 2)
        type_time_layout.addLayout(v_time, 1)
        layout.addLayout(type_time_layout)

        # --- Section: Answer Details ---
        self.stack = QStackedWidget()
        
        # Multiple Choice
        self.mc_w = QWidget()
        mc_l = QVBoxLayout(self.mc_w)
        mc_l.setContentsMargins(0, 5, 0, 5)
        self.opts = []
        for i in range(4):
            le = QLineEdit(); le.setPlaceholderText(f"Option {i+1}")
            le.textChanged.connect(self.set_modified)
            mc_l.addWidget(le); self.opts.append(le)
        
        self.correct_c = QComboBox()
        self.correct_c.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        mc_l.addWidget(QLabel("Correct Option:")); mc_l.addWidget(self.correct_c)
        
        # Identification
        self.id_w = QWidget(); id_l = QVBoxLayout(self.id_w)
        id_l.setContentsMargins(0, 5, 0, 5)
        id_l.addWidget(QLabel("Correct Answer:"))
        self.id_ans = QLineEdit(); self.id_ans.setPlaceholderText("Answer phrase...")
        self.id_ans.textChanged.connect(self.set_modified)
        id_l.addWidget(self.id_ans); id_l.addStretch() 

        self.stack.addWidget(self.mc_w); self.stack.addWidget(self.id_w)
        layout.addWidget(self.stack)

        # --- Action Buttons ---
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add to Quiz")
        self.add_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; height: 30px;")
        self.add_btn.clicked.connect(self.save_question)
        self.cancel_btn = QPushButton("Cancel Edit"); self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.clear_inputs)
        btn_layout.addWidget(self.add_btn); btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))

        # --- Preview ---
        layout.addWidget(QLabel("<b>QUIZ PREVIEW (Numbered)</b>"))
        self.q_list = QListWidget()
        self.q_list.itemClicked.connect(self.load_for_edit)
        layout.addWidget(self.q_list)

        # --- File Controls ---
        file_btns_top = QHBoxLayout()
        self.import_btn = QPushButton("📂 Import")
        self.import_btn.clicked.connect(self.import_quiz)
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setStyleSheet("background-color: #f39c12; color: white;")
        self.save_btn.clicked.connect(self.quick_save)
        
        file_btns_top.addWidget(self.import_btn)
        file_btns_top.addWidget(self.save_btn)
        layout.addLayout(file_btns_top)

        file_btns_bot = QHBoxLayout()
        self.export_btn = QPushButton("📤 Export As (New File)")
        self.export_btn.clicked.connect(self.export_quiz)
        
        self.del_btn = QPushButton("🗑️ Delete Selected")
        self.del_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        self.del_btn.clicked.connect(self.delete_question)
        
        file_btns_bot.addWidget(self.export_btn)
        file_btns_bot.addWidget(self.del_btn)
        layout.addLayout(file_btns_bot)

    def on_type_switch(self, index):
        self.stack.setCurrentIndex(index)
        self.set_modified()

    def set_modified(self):
        if not self.has_unsaved_changes:
            self.has_unsaved_changes = True
            self.changed.emit(True)

    def refresh_list(self):
        self.q_list.clear()
        for i, q in enumerate(self.quiz_bank, 1):
            short = "MC" if q["type"] == "Multiple Choice" else "ID"
            time = q.get("time_limit", 30) # Get time for display
            self.q_list.addItem(f"{i}. [{short}] ({time}s) {str(q['question'])[:35]}...")

    def import_quiz(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Quiz", "", "JSON (*.json)")
        if path:
            try:
                with open(path, 'r') as f:
                    self.quiz_bank = json.load(f)
                    self.current_file_path = path 
                    self.refresh_list(); self.clear_inputs()
                    self.has_unsaved_changes = False; self.changed.emit(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load: {e}")

    def quick_save(self):
        if not self.quiz_bank: return False
        if self.current_file_path:
            try:
                with open(self.current_file_path, 'w') as f:
                    json.dump(self.quiz_bank, f, indent=4)
                self.has_unsaved_changes = False
                self.changed.emit(False)
                QMessageBox.information(self, "Success", f"Saved to {os.path.basename(self.current_file_path)}")
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save: {e}")
                return False
        else:
            return self.export_quiz()

    def export_quiz(self):
        if not self.quiz_bank: return False
        path, _ = QFileDialog.getSaveFileName(self, "Export Quiz", "", "JSON (*.json)")
        if path:
            self.current_file_path = path 
            return self.quick_save()
        return False

    def save_question(self):
        prompt = self.q_input.toPlainText().strip()
        if not prompt: return
        
        # Modified to include time_limit
        data: dict[str, object] = {
            "type": self.type_sel.currentText(), 
            "question": prompt,
            "time_limit": self.time_limit.value() 
        }
        
        if data["type"] == "Multiple Choice":
            opts = [o.text().strip() for o in self.opts]
            data["options"], data["answer"] = opts, opts[self.correct_c.currentIndex()]
        else:
            data["answer"] = self.id_ans.text().strip()
            
        if self.editing_index == -1: self.quiz_bank.append(data)
        else: self.quiz_bank[self.editing_index] = data
        
        self.refresh_list(); self.clear_inputs(); self.set_modified()

    def load_for_edit(self, item):
        self.editing_index = self.q_list.row(item)
        q = self.quiz_bank[self.editing_index]
        
        self.q_input.setPlainText(str(q["question"]))
        self.type_sel.setCurrentText(str(q["type"]))
        # Load time limit
        self.time_limit.setValue(int(q.get("time_limit", 30)))
        
        if q["type"] == "Multiple Choice":
            for i, opt in enumerate(q.get("options", [])): 
                if i < 4: self.opts[i].setText(str(opt))
            if q["answer"] in q.get("options", []):
                self.correct_c.setCurrentIndex(q["options"].index(q["answer"]))
        else: self.id_ans.setText(str(q["answer"]))
        
        self.add_btn.setText("Update Question"); self.cancel_btn.setVisible(True)

    def delete_question(self):
        idx = self.q_list.currentRow()
        if idx >= 0:
            self.quiz_bank.pop(idx)
            self.refresh_list(); self.clear_inputs(); self.set_modified()

    def clear_inputs(self):
        self.editing_index = -1; self.q_input.clear(); self.id_ans.clear()
        self.time_limit.setValue(30) # Reset to default
        for o in self.opts: o.clear()
        self.add_btn.setText("Add to Quiz"); self.cancel_btn.setVisible(False)