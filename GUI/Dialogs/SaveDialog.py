"""
Save simulation dialog
"""
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class SaveDialog:
    def __init__(self, parent=None):
        self.parent = parent
    
    def show_save_dialog(self):
        """Show save file dialog"""
        filename, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Save Simulation",
            "",
            "Simulation Files (*.sim);;All Files (*)"
        )
        return filename
    
    def show_save_success_message(self, filename):
        """Show save success message"""
        QMessageBox.information(
            self.parent,
            "Save Complete",
            f"Simulation saved successfully to {filename}"
        )
    
    def show_save_error_message(self, error):
        """Show save error message"""
        QMessageBox.critical(
            self.parent,
            "Save Error",
            f"Failed to save simulation: {error}"
        )
