from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygon
from PyQt5.QtCore import Qt, QPoint
import math
import numpy as np

class RadarRenderer:
    def __init__(self):
        self.radar_enabled = False
        self.sweep_speed = 2  # Initialize as NUMERIC VALUE, not string
        self.radar_angle = 0
        self.radar_radius = 200
        self.sweep_width = 50  # degrees
        self.detected_obstacles = []

        self.sweep_modes = {
            'slow': 1,   # 1 degree per update
            'normal': 2, # 2 degrees per update
            'fast': 4,    # 4 degrees per update
            'very_fast': 8,  # 8 degrees per update
            'ultra_fast': 16  # 16 degrees per update
        }
        
    def enable_radar(self, enabled: bool):
        self.radar_enabled = enabled

    def set_sweep_speed(self, speed: str):
        """
        Set the radar sweep speed based on predefined modes.
        Available modes: 'slow', 'normal', 'fast', 'very_fast', 'ultra_fast'.
        If an invalid mode is provided, no change is made.
        """
        if speed in self.sweep_modes:
            self.sweep_speed = self.sweep_modes[speed]  # This sets the NUMERIC value
            print(f"Radar sweep speed set to {speed} ({self.sweep_speed} degrees per update)")
        else:
            print(f"Invalid speed mode: {speed}. Using default 'normal'.")
            self.sweep_speed = self.sweep_modes['normal']  # Set numeric value, not string

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
        
        # Check obstacles against ALL active drones (handle empty obstacles list)
        if obstacles:  # Only process if obstacles exist
            for obs in obstacles:
                # Handle different obstacle types
                try:
                    if hasattr(obs, 'x') and hasattr(obs, 'y'):
                        # QRect-like obstacle
                        obs_pos = np.array([obs.x() + obs.width()/2, obs.y() + obs.height()/2])
                    elif hasattr(obs, 'position') and hasattr(obs, 'size'):
                        # Custom obstacle
                        x, y = obs.position
                        size = obs.size if hasattr(obs.size, '__len__') else (obs.size, obs.size)
                        obs_pos = np.array([x + size[0]/2, y + size[1]/2])
                    else:
                        continue  # Skip unknown obstacle types
                    
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
                                if not detected_by_any_drone:  # Only process once per obstacle
                                    visible_obstacles.append(obs_pos)
                                    
                                    # Mark obstacle as spotted (removed debug print)
                                    if hasattr(obs, 'is_spotted'):
                                        obs.is_spotted(obs_pos, self.radar_radius)
                                    else:
                                        obs.spotted_by_radar = True
                                    
                                detected_by_any_drone = True
                                break  # Stop checking other drones for this obstacle
                
                except Exception as e:
                    continue
        
        # Handle both single target and multiple targets
        targets_to_check = []
        
        if target is not None:
            try:
                iter(target)
                if isinstance(target, str):
                    targets_to_check = [target]
                else:
                    targets_to_check = list(target)
            except TypeError:
                targets_to_check = [target]
        
        # Process all targets (whether single or multiple)
        for enemy in targets_to_check:
            if not enemy:
                continue
                
            try:
                # Handle different position formats
                if hasattr(enemy, 'position') and hasattr(enemy, 'width') and hasattr(enemy, 'height'):
                    enemy_pos = np.array([enemy.position[0] + enemy.width/2, enemy.position[1] + enemy.height/2])
                elif hasattr(enemy, 'x') and hasattr(enemy, 'y') and hasattr(enemy, 'width') and hasattr(enemy, 'height'):
                    enemy_pos = np.array([enemy.x() + enemy.width()/2, enemy.y() + enemy.height()/2])
                else:
                    continue

                detected_by_any_drone = False

                for drone in active_drones:
                    radar_center = drone.position
                    distance = np.linalg.norm(enemy_pos - radar_center)

                    if distance <= self.radar_radius:
                        angle_to_enemy = self.get_angle_to_position(radar_center, enemy_pos)

                        if self.is_in_sweep(angle_to_enemy):
                            if not detected_by_any_drone:
                                visible_obstacles.append(enemy_pos)
                                
                                # MARK TARGET AS SPOTTED BY RADAR (removed debug print)
                                enemy.spotted_by_radar = True
                                
                                if hasattr(enemy, 'is_spotted'):
                                    enemy.is_spotted(enemy_pos, self.radar_radius)
                                
                            detected_by_any_drone = True
                            break
            
            except Exception as e:
                continue

        # Advance radar sweep
        try:
            self.radar_angle = (self.radar_angle + self.sweep_speed) % 360
        except TypeError as e:
            # Force numeric values (removed debug prints)
            self.radar_angle = int(self.radar_angle) if isinstance(self.radar_angle, (int, float, str)) else 0
            self.sweep_speed = 2
            self.radar_angle = (self.radar_angle + self.sweep_speed) % 360
        
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

    def render_radar(self, painter, drones, target):
        """Render radar sweeps for drones"""
        if not drones:
            return
            
        try:
            for drone in drones:
                if hasattr(drone, 'radar') and drone.radar and hasattr(drone.radar, 'active') and drone.radar.active:
                    self.draw_radar_sweep(painter, drone)
        except Exception as e:
            print(f"Error in render_radar: {e}")
    
    def draw_radar_sweep(self, painter, radar_center):
        """Draw radar sweep line - FIXED to prevent artifacts"""
        if not self.radar_enabled:
            return
        
        # Calculate sweep line end point
        sweep_angle_rad = math.radians(self.radar_angle)
        end_x = radar_center[0] + self.radar_radius * math.cos(sweep_angle_rad)
        end_y = radar_center[1] + self.radar_radius * math.sin(sweep_angle_rad)
        
        # Draw main sweep line
        painter.setPen(QPen(QColor(0, 255, 0, 200), 2))
        painter.drawLine(
            int(radar_center[0]),
            int(radar_center[1]),
            int(end_x),
            int(end_y)
        )
        
        # Draw sweep sector (arc) - SIMPLIFIED to prevent artifacts
        sweep_width_half = self.sweep_width / 2
        
        # Calculate multiple lines for the sweep sector instead of using drawPie
        num_lines = 5  # Number of lines in the sweep
        for i in range(num_lines):
            line_angle = self.radar_angle - sweep_width_half + (i * self.sweep_width / (num_lines - 1))
            line_angle_rad = math.radians(line_angle)
            
            line_end_x = radar_center[0] + self.radar_radius * math.cos(line_angle_rad)
            line_end_y = radar_center[1] + self.radar_radius * math.sin(line_angle_rad)
            
            # Draw fading sweep lines
            alpha = 100 - (i * 15)  # Fading effect
            painter.setPen(QPen(QColor(0, 255, 0, alpha), 1))
            painter.drawLine(
                int(radar_center[0]),
                int(radar_center[1]),
                int(line_end_x),
                int(line_end_y)
            )
    
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