"""Radar rendering for the drone simulation"""
from PyQt5.QtGui import QPen, QBrush, QPainter
from PyQt5.QtCore import Qt
import math

class RadarRenderer:
    """Renderer for radar display and effects"""
    
    def __init__(self):
        """Initialize radar renderer"""
        self.enabled = False
        self.sweep_angle = 0
        self.sweep_speed = 2.0
        self.radar_range = 150
        
        # Colors
        self.radar_color = Qt.green
        self.sweep_color = Qt.cyan
        self.detection_color = Qt.yellow
        
    def toggle_radar(self):
        """Toggle radar display on/off"""
        self.enabled = not self.enabled
        print(f"Radar {'enabled' if self.enabled else 'disabled'}")
        return self.enabled
    
    def set_sweep_speed(self, speed_mode):
        """Set radar sweep speed"""
        speed_map = {
            "slow": 0.5,
            "normal": 1.0,
            "fast": 2.0,
            "very_fast": 3.0,
            "ultra_fast": 5.0
        }
        self.sweep_speed = speed_map.get(speed_mode.lower().replace(" ", "_"), 1.0)
        print(f"Radar sweep speed set to: {speed_mode}")
    
    def draw_radar(self, painter, offset_y, drones, targets=None):
        """Draw radar sweep and detection"""
        if not self.enabled:
            return
        
        try:
            # Update sweep angle
            self.sweep_angle += self.sweep_speed
            if self.sweep_angle >= 360:
                self.sweep_angle = 0
            
            # Draw radar for each active drone
            for drone in drones:
                if not getattr(drone, 'alive', True):
                    continue
                    
                drone_x = getattr(drone, 'x', 100)
                drone_y = getattr(drone, 'y', 100) + offset_y
                
                # Draw radar range circle (faint)
                painter.setPen(QPen(self.sweep_color, 1, Qt.DashLine))
                painter.setBrush(QBrush())
                painter.drawEllipse(
                    int(drone_x - self.radar_range), 
                    int(drone_y - self.radar_range),
                    int(self.radar_range * 2), 
                    int(self.radar_range * 2)
                )
                
                # Draw radar sweep line
                sweep_rad = math.radians(self.sweep_angle)
                end_x = drone_x + self.radar_range * math.cos(sweep_rad)
                end_y = drone_y + self.radar_range * math.sin(sweep_rad)
                
                painter.setPen(QPen(self.radar_color, 2))
                painter.drawLine(int(drone_x), int(drone_y), int(end_x), int(end_y))
                
                # Draw sweep arc (30-degree cone)
                painter.setPen(QPen(self.radar_color, 1))
                painter.setBrush(QBrush(self.radar_color, Qt.Dense6Pattern))
                
                # Draw radar cone
                cone_angle = 30  # degrees
                start_angle = int((self.sweep_angle - cone_angle/2) * 16)  # Qt uses 16ths of degree
                span_angle = int(cone_angle * 16)
                
                painter.drawPie(
                    int(drone_x - self.radar_range/3), 
                    int(drone_y - self.radar_range/3),
                    int(self.radar_range * 2/3), 
                    int(self.radar_range * 2/3),
                    start_angle, span_angle
                )
                
        except Exception as e:
            print(f"Error in radar rendering: {e}")
    
    def detect_targets(self, drone, targets):
        """Check if targets are within radar detection"""
        detections = []
        
        if not self.enabled or not getattr(drone, 'alive', True):
            return detections
        
        drone_x = getattr(drone, 'x', 0)
        drone_y = getattr(drone, 'y', 0)
        
        for target in targets:
            if hasattr(target, 'x') and hasattr(target, 'y'):
                target_x = target.x()
                target_y = target.y()
                
                # Calculate distance
                distance = math.sqrt((target_x - drone_x)**2 + (target_y - drone_y)**2)
                
                if distance <= self.radar_range:
                    # Calculate angle to target
                    angle = math.degrees(math.atan2(target_y - drone_y, target_x - drone_x))
                    if angle < 0:
                        angle += 360
                    
                    # Check if target is in radar sweep cone
                    cone_angle = 30
                    angle_diff = abs(angle - self.sweep_angle)
                    if angle_diff > 180:
                        angle_diff = 360 - angle_diff
                    
                    if angle_diff <= cone_angle/2:
                        detections.append({
                            'target': target,
                            'distance': distance,
                            'angle': angle
                        })
        
        return detections
    
    def draw_detections(self, painter, offset_y, detections):
        """Draw detected targets"""
        painter.setPen(QPen(self.detection_color, 3))
        painter.setBrush(QBrush(self.detection_color))
        
        for detection in detections:
            target = detection['target']
            if hasattr(target, 'x') and hasattr(target, 'y'):
                x = target.x()
                y = target.y() + offset_y
                
                # Draw detection highlight
                painter.drawEllipse(int(x-8), int(y-8), 16, 16)
    
    def update(self, dt):
        """Update radar state"""
        if self.enabled:
            self.sweep_angle += self.sweep_speed * dt * 60
            if self.sweep_angle >= 360:
                self.sweep_angle = 0