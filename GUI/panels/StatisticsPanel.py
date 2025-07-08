"""Statistics panel for the GUI"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class StatisticsPanel(QWidget):
    """Panel for displaying simulation statistics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        self.drone_count_label = QLabel("Drones: 0")
        self.target_count_label = QLabel("Targets: 0")
        self.mission_status_label = QLabel("Status: Ready")
        
        layout.addWidget(self.drone_count_label)
        layout.addWidget(self.target_count_label)
        layout.addWidget(self.mission_status_label)
        
        self.setLayout(layout)
        self.is_visible = False
    
    def update_statistics(self, stats):
        """Update displayed statistics"""
        if 'drones_count' in stats:
            self.drone_count_label.setText(f"Drones: {stats['drones_count']}")
        if 'targets_count' in stats:
            self.target_count_label.setText(f"Targets: {stats['targets_count']}")
        if 'running' in stats:
            status = "Running" if stats['running'] else "Stopped"
            self.mission_status_label.setText(f"Status: {status}")
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
    
    def update_statistics(self, drones, movement_controller):
        """Update statistics with current simulation data"""
        total_drones = len(drones)
        active_drones = len([d for d in drones if d.alive])
        landed_drones = len([d for d in drones if hasattr(d, 'has_landed') and d.has_landed])
        
        self.drone_count_label.setText(f"Drones: {active_drones}/{total_drones} active")
        
        if hasattr(movement_controller, 'target') and movement_controller.target:
            target_status = "Active" if not getattr(movement_controller.target, 'destroyed', False) else "Destroyed"
            self.target_count_label.setText(f"Target: {target_status}")
        
        mission_status = "Active" if active_drones > 0 else "Complete"
        self.mission_status_label.setText(f"Mission: {mission_status}")
