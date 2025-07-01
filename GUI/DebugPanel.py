import numpy as np
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

class DebugPanel:
    def __init__(self, parent):
        self.parent = parent
        self.debug_label = None
        self.is_visible = False

    def create_panel(self):
        """Create debug information panel"""
        if not self.debug_label:
            self.debug_label = QLabel("Debug Info")
            self.debug_label.setStyleSheet(
                "font-size: 10px; color: black; background-color: rgba(255,255,255,200); "
                "padding: 5px; border: 1px solid gray; border-radius: 3px;"
            )
            self.debug_label.setFixedSize(200, 100)
            self.debug_label.move(900, 100)  # Position in top-right
            self.debug_label.setParent(self.parent)
        
        self.debug_label.show()
        self.is_visible = True

    def hide_panel(self):
        """Hide debug information panel"""
        if self.debug_label:
            self.debug_label.hide()
        self.is_visible = False

    def update_info(self, drones, movement_controller):
        """Update debug panel with current information"""
        if self.is_visible and self.debug_label:
            active_drones = sum(1 for drone in drones if drone.alive)
            total_missiles = sum(len(getattr(drone, 'missiles', [])) for drone in drones)
            pathfinding_active = sum(1 for drone in drones if hasattr(drone, 'current_path') and drone.current_path)
            
            debug_text = f"""Debug Info:
                                Active Drones: {active_drones}
                                Total Missiles: {total_missiles}
                                Pathfinding: {pathfinding_active}
                                Grid Cells: {len(getattr(movement_controller, 'grid', {}))}
                                Frame Rate: ~20 FPS"""
            
            self.debug_label.setText(debug_text)