from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
import numpy as np

class ZoomableSimulationCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Zoom and pan settings
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.pan_offset = QPoint(0, 0)
        
        # Mouse interaction
        self.last_mouse_pos = QPoint()
        self.is_panning = False
        
        # Simulation components (will be set by MainWindow)
        self.sim_manager = None
        self.movement_controller = None
        self.renderer = None
        self.missile_renderer = None
        self.radar_renderer = None
        self.explosion_manager = None
        self.screen_flash = None
        
        # Display options
        self.show_grid = False
        self.show_paths = False
        self.show_debug = False
        
        # Set minimum size
        self.setMinimumSize(800, 600)

    def paintEvent(self, event):
        """Paint the simulation canvas"""
        print("=== CANVAS PAINT EVENT ===")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        # Apply zoom and pan transformations
        painter.scale(self.zoom_factor, self.zoom_factor)
        painter.translate(self.pan_offset.x() / self.zoom_factor, self.pan_offset.y() / self.zoom_factor)
        
        try:
            if hasattr(self, 'sim_manager') and self.sim_manager:
                # Draw simulation elements
                
                print(f"Drawing {len(self.sim_manager.drones)} drones")
                print(f"Drawing {len(self.sim_manager.obstacles)} obstacles")
                
                # Draw base
                if self.sim_manager.base:
                    painter.setBrush(QBrush(QColor(0, 255, 0)))
                    painter.setPen(QPen(QColor(0, 100, 0), 2))
                    painter.drawRect(self.sim_manager.base)
                    print(f"Drew base at {self.sim_manager.base.x()}, {self.sim_manager.base.y()}")
                
                # Draw obstacles - FIXED
                painter.setBrush(QBrush(QColor(139, 69, 19)))
                painter.setPen(QPen(QColor(100, 50, 0), 2))
                for i, obstacle in enumerate(self.sim_manager.obstacles):
                    try:
                        if hasattr(obstacle, 'rect'):
                            painter.drawRect(obstacle.rect)
                        elif hasattr(obstacle, 'x') and hasattr(obstacle, 'y') and hasattr(obstacle, 'width') and hasattr(obstacle, 'height'):
                            painter.drawRect(obstacle.x(), obstacle.y(), obstacle.width(), obstacle.height())
                        elif hasattr(obstacle, 'position') and hasattr(obstacle, 'size'):
                            x, y = obstacle.position
                            w, h = obstacle.size if hasattr(obstacle.size, '__len__') else (obstacle.size, obstacle.size)
                            painter.drawRect(int(x), int(y), int(w), int(h))
                        else:
                            painter.drawRect(100 + i * 50, 100, 40, 40)
                        print(f"Drew obstacle {i}")
                    except Exception as e:
                        print(f"Error drawing obstacle {i}: {e}")
                        painter.drawRect(100 + i * 50, 100, 40, 40)
        
                # Draw drones
                painter.setBrush(QBrush(QColor(0, 0, 255)))
                painter.setPen(QPen(QColor(0, 0, 200), 2))
                for i, drone in enumerate(self.sim_manager.drones):
                    x = int(drone.position[0]) - 10
                    y = int(drone.position[1]) - 10
                    painter.drawEllipse(x, y, 20, 20)
                    print(f"Drew drone {i} at {drone.position[0]}, {drone.position[1]}")
                
                # Draw target - FIXED with placeholder handling
                if self.sim_manager.target and not getattr(self.sim_manager.target, 'is_placeholder', False):
                    painter.setBrush(QBrush(QColor(255, 0, 0)))
                    painter.setPen(QPen(QColor(200, 0, 0), 3))
                    
                    target = self.sim_manager.target
                    try:
                        if hasattr(target, 'position') and hasattr(target.position, '__len__') and len(target.position) >= 2:
                            target_pos = target.position
                            x = int(target_pos[0]) - 15
                            y = int(target_pos[1]) - 15
                        elif hasattr(target, 'x') and hasattr(target, 'y'):
                            x = int(target.x()) - 15
                            y = int(target.y()) - 15
                        elif hasattr(target, 'position'):
                            if hasattr(target.position, '__len__'):
                                x = int(target.position[0]) - 15
                                y = int(target.position[1]) - 15
                            else:
                                x = 740 - 15
                                y = int(target.position) - 15
                        else:
                            x = 740 - 15
                            y = 560 - 15
                            
                        painter.drawEllipse(x, y, 30, 30)
                        print(f"Drew target at {x + 15}, {y + 15}")
                        
                    except Exception as e:
                        print(f"Error drawing target: {e}")
                        painter.drawEllipse(725, 545, 30, 30)
                        print("Drew target at fallback position")
                
                # Draw missiles if missile_renderer exists
                if self.missile_renderer and self.movement_controller:
                    try:
                        self.missile_renderer.render_missiles(painter, self.movement_controller.missile_manager)
                        print("Drew missiles")
                    except Exception as e:
                        print(f"Error drawing missiles: {e}")
                
                # Draw radar if enabled
                if self.radar_renderer:
                    try:
                        self.radar_renderer.render_radar(painter, self.sim_manager.drones, self.sim_manager.target)
                        print("Drew radar")
                    except Exception as e:
                        print(f"Error drawing radar: {e}")
            
            else:
                # No simulation data available
                print("No sim_manager available for drawing")
                painter.setPen(QPen(QColor(255, 0, 0), 2))
                painter.drawText(50, 50, "NO SIMULATION DATA")
        
        except Exception as e:
            # Handle errors
            print(f"Error in paintEvent: {e}")
            import traceback
            traceback.print_exc()
        
        print("=== END PAINT EVENT ===")
        painter.end()

    def draw_grid(self, painter):
        """Draw grid lines"""
        grid_size = 20
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        
        # Vertical lines
        for x in range(0, 1200, grid_size):
            painter.drawLine(x, 0, x, 800)
        
        # Horizontal lines
        for y in range(0, 800, grid_size):
            painter.drawLine(0, y, 1200, y)

    def reset_view(self):
        """Reset zoom and pan to defaults"""
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update()

    def fit_to_view(self):
        """Fit all elements to view"""
        if not self.sim_manager or not self.sim_manager.drones:
            return
        
        # Calculate bounding box of all elements
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        # Include drones
        for drone in self.sim_manager.drones:
            min_x = min(min_x, drone.position[0])
            max_x = max(max_x, drone.position[0])
            min_y = min(min_y, drone.position[1])
            max_y = max(max_y, drone.position[1])
        
        # Include target
        if self.sim_manager.target:
            target_pos = getattr(self.sim_manager.target, 'position', [0, 0])
            min_x = min(min_x, target_pos[0])
            max_x = max(max_x, target_pos[0])
            min_y = min(min_y, target_pos[1])
            max_y = max(max_y, target_pos[1])
        
        # Calculate zoom to fit
        if max_x > min_x and max_y > min_y:
            width_ratio = self.width() / (max_x - min_x + 100)
            height_ratio = self.height() / (max_y - min_y + 100)
            self.zoom_factor = min(width_ratio, height_ratio, self.max_zoom)
            
            # Center the view
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            self.pan_offset = QPoint(
                int(self.width() / 2 - center_x * self.zoom_factor),
                int(self.height() / 2 - center_y * self.zoom_factor)
            )
        
        self.update()

    def mousePressEvent(self, event):
        """Handle mouse press for panning"""
        if event.button() == Qt.LeftButton:
            self.is_panning = True
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        """Handle mouse move for panning"""
        if self.is_panning:
            delta = event.pos() - self.last_mouse_pos
            self.pan_offset += delta
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.is_panning = False

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        zoom_in = event.angleDelta().y() > 0
        zoom_factor = 1.15 if zoom_in else 1/1.15
        
        new_zoom = self.zoom_factor * zoom_factor
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        
        if new_zoom != self.zoom_factor:
            self.zoom_factor = new_zoom
            self.update()