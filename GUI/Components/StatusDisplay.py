"""
Status display components and utilities
"""
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

class StatusDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the status display UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    def update_status(self, message, color="#000000"):
        """Update the status message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def clear_status(self):
        """Clear the status display"""
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: #000000;")
