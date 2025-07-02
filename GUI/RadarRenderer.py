from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygon
from PyQt5.QtCore import Qt, QPoint
import math
import numpy as np

class RadarRenderer:
    def __init__(self):
        self.radar_enabled = False
        self.radar_angle = 0
        self.radar_radius = 150
        self.sweep_width = 30  # degrees
        self.detected_obstacles = []
        
    def update_radar(self, obstacles, target, drones):
        """Update radar sweep and detect obstacles from ALL active drones"""
        if not self.radar_enabled:
            return []
        
        visible_obstacles = []
        
        # Get ALL active drone positions
        active_drones = []
        for drone in drones:
            if drone.alive and not (hasattr(drone, 'has_landed') and drone.has_landed):
                active_drones.append(drone)
        
        if not active_drones:
            return []
        
        # Check obstacles against ALL active drones
        for obs in obstacles:
            obs_pos = np.array([obs.x() + obs.width()/2, obs.y() + obs.height()/2])
            
            # Check if obstacle is detected by ANY active drone
            detected_by_any_drone = False
            
            for drone in active_drones:
                radar_center = drone.position
                
                # Calculate distance from this drone's radar center
                distance = np.linalg.norm(obs_pos - radar_center)
                
                if distance <= self.radar_radius:
                    # Calculate angle to obstacle from this drone
                    angle_to_obs = self.get_angle_to_position(radar_center, obs_pos)
                    
                    # Check if obstacle is within sweep angle for this drone
                    if self.is_in_sweep(angle_to_obs):
                        if not detected_by_any_drone:  # Only #print once per obstacle
                            visible_obstacles.append(obs_pos)
                            obs.is_spotted(obs_pos, self.radar_radius)
                            #print(f"Radar detected obstacle at ({obs.x()}, {obs.y()}) by drone {drone.drone_id} - distance: {distance:.1f}")
                        detected_by_any_drone = True
                        break  # Stop checking other drones for this obstacle
        
        # Handle both single target and multiple targets
        targets_to_check = []
        
        if target is not None:
            # Check if target is iterable (list/tuple) or single object
            try:
                # Try to iterate - if it works, it's a collection
                iter(target)
                # If target is a string, treat it as single object (strings are iterable but we don't want to iterate chars)
                if isinstance(target, str):
                    targets_to_check = [target]
                else:
                    targets_to_check = list(target)
            except TypeError:
                # Not iterable, single target
                targets_to_check = [target]
        
        # Process all targets (whether single or multiple)
        for enemy in targets_to_check:
            # Skip if target doesn't exist or no position data
            if not enemy:
                continue
                
            # Handle different position formats
            if hasattr(enemy, 'position') and hasattr(enemy, 'width') and hasattr(enemy, 'height'):
                # Target with position array and width/height
                enemy_pos = np.array([enemy.position[0] + enemy.width/2, enemy.position[1] + enemy.height/2])
            elif hasattr(enemy, 'x') and hasattr(enemy, 'y') and hasattr(enemy, 'width') and hasattr(enemy, 'height'):
                # Target with x(),y() methods
                enemy_pos = np.array([enemy.x() + enemy.width()/2, enemy.y() + enemy.height()/2])
            else:
                # Skip if we can't determine position
                continue

            detected_by_any_drone = False

            for drone in active_drones:
                radar_center = drone.position

                # Calculate distance from this drone's radar center
                distance = np.linalg.norm(enemy_pos - radar_center)

                if distance <= self.radar_radius:
                    # Calculate angle to enemy from this drone
                    angle_to_enemy = self.get_angle_to_position(radar_center, enemy_pos)

                    # Check if enemy is within sweep angle for this drone
                    if self.is_in_sweep(angle_to_enemy):
                        if not detected_by_any_drone:
                            visible_obstacles.append(enemy_pos)
                            
                            # MARK TARGET AS SPOTTED BY RADAR
                            enemy.spotted_by_radar = True
                            
                            if hasattr(enemy, 'is_spotted'):
                                enemy.is_spotted(enemy_pos, self.radar_radius)
                            
                            # Handle different position access methods for logging
                            if hasattr(enemy, 'position'):
                                print(f"🎯 RADAR SPOTTED TARGET at ({enemy.position[0]:.1f}, {enemy.position[1]:.1f}) by drone {drone.drone_id} - distance: {distance:.1f}")
                            else:
                                print(f"🎯 RADAR SPOTTED TARGET at ({enemy.x():.1f}, {enemy.y():.1f}) by drone {drone.drone_id} - distance: {distance:.1f}")
                        detected_by_any_drone = True
                        break  # Stop checking other drones for this enemy

        
        # Advance radar sweep
        self.radar_angle = (self.radar_angle + 2) % 360
        
        return visible_obstacles
    
    def get_angle_to_position(self, center, target):
        """Calculate angle from center to target position"""
        dx = target[0] - center[0]
        dy = target[1] - center[1]
        return math.degrees(math.atan2(dy, dx)) % 360
    
    def is_in_sweep(self, target_angle):
        """Check if target angle is within radar sweep"""
        # Handle wrap-around cases
        diff = abs(target_angle - self.radar_angle)
        if diff > 180:
            diff = 360 - diff
        return diff <= self.sweep_width / 2
    
    def draw_radar(self, painter, drones, obstacles, offset_y):
        """Draw radar overlay around ALL active drones"""
        if not self.radar_enabled:
            return
        
        # Get ALL active drone positions
        active_drones = []
        for drone in drones:
            if drone.alive and not (hasattr(drone, 'has_landed') and drone.has_landed):
                active_drones.append(drone)
        
        if not active_drones:
            return
        
        # Draw radar for EACH active drone
        for drone in active_drones:
            radar_center = (int(drone.position[0]), int(drone.position[1]) + offset_y)
            
            # Draw radar circle for this drone
            painter.setPen(QPen(QColor(0, 255, 0, 100), 2))  # Green, semi-transparent
            painter.setBrush(QBrush(QColor(0, 255, 0, 20)))   # Very transparent fill
            painter.drawEllipse(
                radar_center[0] - self.radar_radius,
                radar_center[1] - self.radar_radius,
                self.radar_radius * 2,
                self.radar_radius * 2
            )
            
            # Draw radar sweep for this drone
            self.draw_radar_sweep(painter, radar_center)
            
            # Draw range rings for this drone
            self.draw_range_rings(painter, radar_center)
        
        # Draw detected obstacles (only once, not per drone)
        self.draw_detected_obstacles(painter, obstacles, offset_y)

    def draw_radar_sweep(self, painter, center):
        """Draw the rotating radar sweep"""
        # Calculate sweep start and end angles
        start_angle = self.radar_angle - self.sweep_width / 2
        end_angle = self.radar_angle + self.sweep_width / 2
        
        # Create sweep polygon
        points = [QPoint(center[0], center[1])]  # Center point
        
        # Add arc points
        for angle in range(int(start_angle), int(end_angle) + 1, 2):
            x = center[0] + self.radar_radius * math.cos(math.radians(angle))
            y = center[1] + self.radar_radius * math.sin(math.radians(angle))
            points.append(QPoint(int(x), int(y)))
        
        # Draw sweep
        polygon = QPolygon(points)
        painter.setPen(QPen(QColor(0, 255, 0, 150), 1))
        painter.setBrush(QBrush(QColor(0, 255, 0, 60)))
        painter.drawPolygon(polygon)
        
        # Draw sweep line
        sweep_end_x = center[0] + self.radar_radius * math.cos(math.radians(self.radar_angle))
        sweep_end_y = center[1] + self.radar_radius * math.sin(math.radians(self.radar_angle))
        painter.setPen(QPen(QColor(0, 255, 0, 200), 3))
        painter.drawLine(center[0], center[1], int(sweep_end_x), int(sweep_end_y))
    
    def draw_detected_obstacles(self, painter, obstacles, offset_y):
        """Draw obstacles that have been detected (updated to not need radar_center)"""
        for obs in obstacles:
            if not obs.is_hidden:  # Obstacle has been detected
                # Draw detection highlight
                painter.setPen(QPen(QColor(255, 255, 0, 200), 3))  # Yellow highlight
                painter.setBrush(QBrush(QColor(255, 255, 0, 50)))
                
                # Draw around the obstacle
                highlight_rect = (
                    obs.x() - 5,
                    obs.y() + offset_y - 5,
                    obs.width() + 10,
                    obs.height() + 10
                )
                painter.drawRect(*highlight_rect)
                
                # Draw detection blip
                obs_center_x = obs.x() + obs.width() / 2
                obs_center_y = obs.y() + obs.height() / 2 + offset_y
                painter.setBrush(QBrush(QColor(255, 0, 0)))
                painter.drawEllipse(int(obs_center_x) - 3, int(obs_center_y) - 3, 6, 6)
    
    def draw_range_rings(self, painter, center):
        """Draw range rings on radar"""
        painter.setPen(QPen(QColor(0, 255, 0, 80), 1))
        painter.setBrush(QBrush(Qt.transparent))
        
        # Draw concentric circles at 1/4, 1/2, 3/4 range
        for fraction in [0.25, 0.5, 0.75]:
            radius = int(self.radar_radius * fraction)
            painter.drawEllipse(
                center[0] - radius,
                center[1] - radius,
                radius * 2,
                radius * 2
            )
    
    def toggle_radar(self):
        """Toggle radar on/off"""
        self.radar_enabled = not self.radar_enabled
        return self.radar_enabled