"""Concrete renderer implementation"""
from .Renderer import Renderer
from PyQt5.QtGui import QPen, QBrush, QPainter
from PyQt5.QtCore import Qt

class ConcreteRenderer(Renderer):
    """Concrete implementation of the Renderer class"""
    
    def __init__(self):
        super().__init__()
        self.sim_modes = None
        
    def render(self, painter, objects):
        """Render objects using the painter"""
        # Basic rendering implementation
        painter.setPen(QPen(Qt.black, 1))
        
        for obj in objects:
            if hasattr(obj, 'x') and hasattr(obj, 'y'):
                x, y = obj.x(), obj.y()
                size = getattr(obj, 'size', 10)
                painter.drawEllipse(int(x-size/2), int(y-size/2), size, size)
    
    def draw_grid(self, painter, offset_y, movement_controller):
        """Draw grid on the simulation canvas"""
        painter.setPen(QPen(Qt.lightGray, 1))
        
        # Draw grid lines
        for x in range(0, 1000, 50):
            painter.drawLine(x, offset_y, x, 700)
        for y in range(offset_y, 700, 50):
            painter.drawLine(0, y, 1000, y)
    
    def draw_static_elements(self, painter, offset_y, obstacles, target, base):
        """Draw static elements like obstacles, target, and base"""
        # Draw obstacles
        painter.setPen(QPen(Qt.darkRed, 2))
        painter.setBrush(QBrush(Qt.darkRed))
        
        for obstacle in obstacles:
            painter.drawRect(obstacle.x(), obstacle.y() + offset_y, 
                           obstacle.width(), obstacle.height())
        
        # Draw target
        if target and not getattr(target, 'destroyed', False):
            painter.setPen(QPen(Qt.red, 3))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(int(target.x() - 15), int(target.y() + offset_y - 15), 30, 30)
        
        # Draw base
        if base:
            painter.setPen(QPen(Qt.blue, 3))
            painter.setBrush(QBrush(Qt.blue))
            painter.drawRect(base.x(), base.y() + offset_y, base.width(), base.height())
    
    def draw_drone_with_status(self, painter, drone, offset_y, drone_size):
        """Draw a drone with its status"""
        painter.setPen(QPen(Qt.green, 2))
        painter.setBrush(QBrush(Qt.green))
        
        x, y = drone.x, drone.y
        painter.drawEllipse(int(x - drone_size/2), int(y + offset_y - drone_size/2), 
                          drone_size, drone_size)
        
        # Draw drone ID
        painter.setPen(QPen(Qt.black))
        painter.drawText(int(x - 5), int(y + offset_y - 25), str(drone.drone_id))
    
    def draw_paths(self, painter, offset_y, drones):
        """Draw paths for drones"""
        painter.setPen(QPen(Qt.cyan, 1, Qt.DashLine))
        
        for drone in drones:
            if hasattr(drone, 'path_history') and len(drone.path_history) > 1:
                for i in range(len(drone.path_history) - 1):
                    p1 = drone.path_history[i]
                    p2 = drone.path_history[i + 1]
                    painter.drawLine(int(p1[0]), int(p1[1] + offset_y),
                                   int(p2[0]), int(p2[1] + offset_y))