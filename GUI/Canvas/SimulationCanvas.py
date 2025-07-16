from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMainWindow
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from Config.SimulationConfig import SimulationConfig



class SimulationCanvas(QWidget):
    """Custom widget for drawing the simulation"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setMinimumSize(800, 600)
        
    def paintEvent(self, event):
        """Paint the simulation"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate offset for control panel
        offset_y = SimulationConfig.CONTROL_PANEL_HEIGHT + 15
        
        try:
            # Draw background first
            painter.fillRect(self.rect(), Qt.white)
            
            # Draw grid if enabled
            if self.main_window.show_grid:
                self.main_window.renderer.draw_grid(painter, offset_y, self.main_window.sim_manager.movement_controller)
            
            # Draw static elements (obstacles, target, base)
            self.main_window.renderer.draw_static_elements(
                painter, offset_y, self.main_window.sim_manager.obstacles, 
                self.main_window.sim_manager.target, self.main_window.sim_manager.base
            )
            
            # Draw radar
            self.main_window.radar_renderer.draw_radar(painter, self.main_window.sim_manager.drones, self.main_window.sim_manager.obstacles, offset_y)
            
            # Draw drones
            for drone in self.main_window.sim_manager.drones:
                if drone.alive:  # Only draw active drones
                    self.main_window.renderer.draw_drone_with_status(painter, drone, offset_y, SimulationConfig.DRONE_SIZE)
            
            # Draw paths if enabled
            if self.main_window.show_paths:
                self.main_window.renderer.draw_paths(painter, offset_y, self.main_window.sim_manager.drones)
            
            # Draw missiles
            if hasattr(self.main_window.sim_manager.movement_controller, 'missile_manager'):
                self.main_window.missile_renderer.draw_missiles(painter, self.main_window.sim_manager.movement_controller.missile_manager, offset_y)
            
            # Draw explosion effects
            self.main_window.explosion_manager.draw_all(painter, SimulationConfig.CONTROL_PANEL_HEIGHT)
            self.main_window.screen_flash.draw(painter, self.width(), self.height())
            
        except Exception as e:
            print(f"Error in paintEvent: {e}")
            # Draw error message
            painter.setPen(Qt.red)
            painter.drawText(50, 100, f"Rendering Error: {str(e)}")
        
        painter.end()
