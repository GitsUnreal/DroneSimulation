"""
Load simulation dialog
"""
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class LoadDialog:
    def __init__(self, parent=None):
        self.parent = parent
    
    def show_load_dialog(self):
        """Show load file dialog"""
        filename, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Load Simulation",
            "",
            "Simulation Files (*.sim);;All Files (*)"
        )
        return filename
    
    def show_load_success_message(self, filename):
        """Show load success message"""
        QMessageBox.information(
            self.parent,
            "Load Complete",
            f"Simulation loaded successfully from {filename}"
        )
    
    def show_load_error_message(self, error):
        """Show load error message"""
        QMessageBox.critical(
            self.parent,
            "Load Error",
            f"Failed to load simulation: {error}"
        )
