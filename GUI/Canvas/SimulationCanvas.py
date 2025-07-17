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
        """Paint the simulation canvas"""
        print("=== CANVAS PAINT EVENT ===")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        print(f"Painter valid: {painter.isActive()}")
        print(f"Canvas rect: {self.rect()}")
        
        # Clear background
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        # Apply zoom and pan transformations
        painter.scale(self.zoom_factor, self.zoom_factor)
        painter.translate(self.pan_offset.x() / self.zoom_factor, self.pan_offset.y() / self.zoom_factor)
        
        try:
            # Draw grid if enabled
            if getattr(self, 'show_grid', False):
                self.draw_grid(painter)
                print("Drew grid")
            
            # Draw simulation elements
            if hasattr(self, 'sim_manager') and self.sim_manager:
                print(f"Drawing {len(self.sim_manager.drones)} drones")
                print(f"Drawing {len(self.sim_manager.obstacles)} obstacles")
                
                # Draw base
                if self.sim_manager.base:
                    painter.setBrush(QBrush(QColor(0, 255, 0)))
                    painter.drawRect(self.sim_manager.base)
                    print("Drew base")
                
                # Draw obstacles
                painter.setBrush(QBrush(QColor(139, 69, 19)))
                for obstacle in self.sim_manager.obstacles:
                    painter.drawRect(obstacle)
                print("Drew obstacles")
                
                # Draw drones
                painter.setBrush(QBrush(QColor(0, 0, 255)))
                for drone in self.sim_manager.drones:
                    drone_rect = QRect(int(drone.position[0]) - 10, int(drone.position[1]) - 10, 20, 20)
                    painter.drawEllipse(drone_rect)
                print("Drew drones")
                
                # Draw target
                if self.sim_manager.target:
                    painter.setBrush(QBrush(QColor(255, 0, 0)))
                    target_pos = getattr(self.sim_manager.target, 'position', [0, 0])
                    target_rect = QRect(int(target_pos[0]) - 15, int(target_pos[1]) - 15, 30, 30)
                    painter.drawEllipse(target_rect)
                    print("Drew target")
            
            else:
                print("No sim_manager available for drawing")
                
        except Exception as e:
            print(f"Error in paintEvent: {e}")
            import traceback
            traceback.print_exc()
        
        print("=== END PAINT EVENT ===")
        painter.end()
