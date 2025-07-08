# drone_system/sensors/RadarSystem.py
import numpy as np
import math

class RadarSystem:
    """Core radar logic for drones"""
    
    def __init__(self, radius=200, sweep_width=50):
        self.radius = radius
        self.sweep_width = sweep_width
        self.sweep_angle = 0
        self.sweep_speed = 2
        self.detected_objects = []
    
    def update_sweep(self):
        """Update radar sweep angle"""
        self.sweep_angle = (self.sweep_angle + self.sweep_speed) % 360
    
    def detect_objects(self, drone_position, objects):
        """Detect objects within radar range and sweep"""
        detected = []
        
        for obj in objects:
            distance = np.linalg.norm(obj.position - drone_position)
            
            if distance <= self.radius:
                angle = self._get_angle_to_object(drone_position, obj.position)
                if self._is_in_sweep(angle):
                    detected.append(obj)
        
        return detected
    
    def _get_angle_to_object(self, from_pos, to_pos):
        """Calculate angle to object"""
        diff = to_pos - from_pos
        return math.degrees(math.atan2(diff[1], diff[0])) % 360
    
    def _is_in_sweep(self, angle):
        """Check if angle is within current sweep"""
        start_angle = (self.sweep_angle - self.sweep_width / 2) % 360
        end_angle = (self.sweep_angle + self.sweep_width / 2) % 360
        
        if start_angle <= end_angle:
            return start_angle <= angle <= end_angle
        else:
            return angle >= start_angle or angle <= end_angle

# gui/rendering/RadarRenderer.py
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygon
from PyQt5.QtCore import Qt, QPoint
import math

class RadarRenderer:
    """GUI rendering for radar display"""
    
    def __init__(self):
        self.enabled = False
        self.sweep_modes = {
            'slow': 1, 'normal': 2, 'fast': 4, 
            'very_fast': 8, 'ultra_fast': 16
        }
    
    def draw_radar_overlay(self, painter, radar_system, drone_position, offset_y):
        """Draw radar overlay for a drone"""
        if not self.enabled:
            return
        
        center = (int(drone_position[0]), int(drone_position[1]) + offset_y)
        
        # Draw radar circle
        painter.setPen(QPen(QColor(0, 255, 0, 100), 2))
        painter.setBrush(QBrush(QColor(0, 255, 0, 20)))
        painter.drawEllipse(
            center[0] - radar_system.radius,
            center[1] - radar_system.radius,
            radar_system.radius * 2,
            radar_system.radius * 2
        )
        
        # Draw sweep
        self._draw_sweep(painter, radar_system, center)
        self._draw_range_rings(painter, radar_system, center)
    
    def _draw_sweep(self, painter, radar_system, center):
        """Draw the radar sweep"""
        start_angle = radar_system.sweep_angle - radar_system.sweep_width / 2
        end_angle = radar_system.sweep_angle + radar_system.sweep_width / 2
        
        points = [QPoint(center[0], center[1])]
        
        for angle in range(int(start_angle), int(end_angle) + 1, 2):
            x = center[0] + radar_system.radius * math.cos(math.radians(angle))
            y = center[1] + radar_system.radius * math.sin(math.radians(angle))
            points.append(QPoint(int(x), int(y)))
        
        polygon = QPolygon(points)
        painter.setPen(QPen(QColor(0, 255, 0, 150), 1))
        painter.setBrush(QBrush(QColor(0, 255, 0, 60)))
        painter.drawPolygon(polygon)
    
    def _draw_range_rings(self, painter, radar_system, center):
        """Draw range rings"""
        painter.setPen(QPen(QColor(0, 255, 0, 80), 1))
        painter.setBrush(QBrush(Qt.transparent))
        
        for fraction in [0.25, 0.5, 0.75]:
            radius = int(radar_system.radius * fraction)
            painter.drawEllipse(
                center[0] - radius, center[1] - radius,
                radius * 2, radius * 2
            )
    
    def toggle(self):
        """Toggle radar display"""
        self.enabled = not self.enabled
        return self.enabled