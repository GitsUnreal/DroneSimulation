"""Debug panel for the GUI"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class DebugPanel(QWidget):
    """Debug information panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        self.debug_label = QLabel("Debug Information:")
        self.debug_text = QTextEdit()
        self.debug_text.setMaximumHeight(200)
        
        layout.addWidget(self.debug_label)
        layout.addWidget(self.debug_text)
        
        self.setLayout(layout)
    
    def add_debug_message(self, message):
        """Add a debug message"""
        self.debug_text.append(message)
    
    def clear_debug(self):
        """Clear debug messages"""
        self.debug_text.clear()