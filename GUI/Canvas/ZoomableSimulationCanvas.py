from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen
from PyQt5.QtCore import Qt
from .SimulationDrawingMixin import SimulationDrawingMixin

class ZoomableSimulationCanvas(QWidget, SimulationDrawingMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Use safer attributes
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StaticContents, True)
        
        # Initialize properties
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.pan_offset = [0, 0]
        
        # Mouse interaction state
        self.last_pan_point = None
        self.is_panning = False
        
        # Initialize simulation references
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

    def mousePressEvent(self, event):
        """Handle mouse press events for panning"""
        if event.button() == Qt.LeftButton:
            # Start panning with left click
            self.last_pan_point = [event.x(), event.y()]
            self.is_panning = True
            self.setCursor(Qt.ClosedHandCursor)  # Change cursor to indicate dragging

    def mouseMoveEvent(self, event):
        """Handle mouse move events for panning"""
        if self.is_panning and self.last_pan_point:
            # Calculate how much the mouse moved
            delta_x = event.x() - self.last_pan_point[0]
            delta_y = event.y() - self.last_pan_point[1]
            
            # Update pan offset
            self.pan_offset[0] += delta_x
            self.pan_offset[1] += delta_y
            
            # Update last pan point
            self.last_pan_point = [event.x(), event.y()]
            
            # Redraw the canvas
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.LeftButton:
            # Stop panning
            self.is_panning = False
            self.last_pan_point = None
            self.setCursor(Qt.ArrowCursor)  # Reset cursor

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        zoom_in = event.angleDelta().y() > 0
        zoom_factor = 1.1 if zoom_in else 1/1.1
        
        old_zoom = self.zoom_factor
        new_zoom = old_zoom * zoom_factor
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        
        if new_zoom != old_zoom:
            # Zoom towards mouse cursor
            mouse_x = event.x()
            mouse_y = event.y()
            
            # Calculate world position before zoom
            world_x_before = (mouse_x - self.pan_offset[0]) / old_zoom
            world_y_before = (mouse_y - self.pan_offset[1]) / old_zoom
            
            # Update zoom
            self.zoom_factor = new_zoom
            
            # Calculate world position after zoom
            world_x_after = (mouse_x - self.pan_offset[0]) / new_zoom
            world_y_after = (mouse_y - self.pan_offset[1]) / new_zoom
            
            # Adjust pan to keep mouse position stable
            self.pan_offset[0] += (world_x_after - world_x_before) * new_zoom
            self.pan_offset[1] += (world_y_after - world_y_before) * new_zoom
            
            self.update()

    def reset_view(self):
        """Reset the view to default zoom and position"""
        self.zoom_factor = 1.0
        self.pan_offset = [0, 0]
        self.update()

    def fit_to_view(self):
        """Fit all simulation elements to view"""
        if not self.sim_manager or not self.sim_manager.drones:
            return
        
        # Calculate bounding box of all elements
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        # Check drones
        for drone in self.sim_manager.drones:
            min_x = min(min_x, drone.position[0])
            max_x = max(max_x, drone.position[0])
            min_y = min(min_y, drone.position[1])
            max_y = max(max_y, drone.position[1])
        
        # Check target
        if self.sim_manager.target and hasattr(self.sim_manager.target, 'position'):
            min_x = min(min_x, self.sim_manager.target.position[0])
            max_x = max(max_x, self.sim_manager.target.position[0])
            min_y = min(min_y, self.sim_manager.target.position[1])
            max_y = max(max_y, self.sim_manager.target.position[1])
        
        # Check obstacles
        for obs in self.sim_manager.obstacles:
            if hasattr(obs, 'x') and hasattr(obs, 'y'):
                min_x = min(min_x, obs.x())
                max_x = max(max_x, obs.x() + obs.width())
                min_y = min(min_y, obs.y())
                max_y = max(max_y, obs.y() + obs.height())
        
        # Check base
        if self.sim_manager.base:
            min_x = min(min_x, self.sim_manager.base.x())
            max_x = max(max_x, self.sim_manager.base.x() + self.sim_manager.base.width())
            min_y = min(min_y, self.sim_manager.base.y())
            max_y = max(max_y, self.sim_manager.base.y() + self.sim_manager.base.height())
        
        # Add padding
        padding = 100
        content_width = max_x - min_x + 2 * padding
        content_height = max_y - min_y + 2 * padding
        
        # Calculate zoom to fit
        zoom_x = self.width() / content_width if content_width > 0 else 1
        zoom_y = self.height() / content_height if content_height > 0 else 1
        zoom = min(zoom_x, zoom_y, self.max_zoom)
        
        # Center the view
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        self.zoom_factor = zoom
        self.pan_offset[0] = self.width() / 2 - center_x * zoom
        self.pan_offset[1] = self.height() / 2 - center_y * zoom
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return
        try:
            painter.fillRect(self.rect(), QColor(240, 240, 240))
            pen = QPen(QColor(80, 80, 80), 3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
            painter.scale(self.zoom_factor, self.zoom_factor)
            painter.translate(self.pan_offset[0] / self.zoom_factor, self.pan_offset[1] / self.zoom_factor)
            if self.sim_manager:
                self.draw_simulation_elements(painter, self.sim_manager)
        except Exception:
            pass
        finally:
            painter.end()