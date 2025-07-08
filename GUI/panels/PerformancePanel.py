"""Performance monitoring panel"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
import time

class PerformancePanel(QWidget):
    """Panel for displaying performance metrics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.last_update = time.time()
        self.frame_count = 0
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        self.fps_label = QLabel("FPS: 0")
        self.frame_time_label = QLabel("Frame Time: 0ms")
        
        layout.addWidget(self.fps_label)
        layout.addWidget(self.frame_time_label)
        
        self.setLayout(layout)
        self.is_visible = False
    
    def update_performance(self, dt):
        """Update performance metrics"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_update >= 1.0:  # Update every second
            fps = self.frame_count / (current_time - self.last_update)
            frame_time = dt * 1000  # Convert to milliseconds
            
            self.fps_label.setText(f"FPS: {fps:.1f}")
            self.frame_time_label.setText(f"Frame Time: {frame_time:.1f}ms")
            
            self.last_update = current_time
            self.frame_count = 0
    def toggle_panel(self):
        """Toggle panel visibility"""
        if self.isVisible():
            self.hide()
            self.is_visible = False
        else:
            self.show()
            self.is_visible = True
    
    def show_panel(self):
        """Show the panel"""
        self.show()
        self.is_visible = True
    
    def hide_panel(self):
        """Hide the panel"""
        self.hide()
        self.is_visible = False
    
    def update_metrics(self, drones, movement_controller):
        """Update performance metrics with drone data"""
        active_drones = len([d for d in drones if d.alive])
        total_missiles = sum(d.missiles_fired for d in drones)
        
        self.fps_label.setText(f"Active Drones: {active_drones}")
        self.frame_time_label.setText(f"Total Missiles Fired: {total_missiles}")
