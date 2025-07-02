from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import QRect
import numpy as np

class Renderer:
    def __init__(self):
        pass

    def draw_grid(self, painter, offset_y, movement_controller):
        """Draw the pathfinding grid overlay"""
        painter.setPen(QColor(200, 200, 200, 100))  # Light gray, semi-transparent
        
        cell_size = 20  # Match your grid cell size
        width, height = 1080, 720 - offset_y
        
        # Draw vertical lines
        for x in range(0, width, cell_size):
            painter.drawLine(x, offset_y, x, height + offset_y)
        
        # Draw horizontal lines
        for y in range(offset_y, height + offset_y, cell_size):
            painter.drawLine(0, y, width, y)
        
        # Highlight blocked cells
        painter.setBrush(QColor(255, 0, 0, 50))  # Red, semi-transparent
        painter.setPen(QColor(255, 0, 0, 100))
        
        if hasattr(movement_controller, 'grid'):
            for (x, y), data in movement_controller.grid.items():
                if data['blocked']:
                    painter.drawRect(x, y + offset_y, cell_size, cell_size)

    def draw_paths(self, painter, offset_y, drones):
        """Draw drone paths for debugging - but skip landed drones"""
        colors = [
            QColor(255, 100, 100),  # Red
            QColor(100, 255, 100),  # Green
            QColor(100, 100, 255),  # Blue
            QColor(255, 255, 100),  # Yellow
            QColor(255, 100, 255),  # Magenta
        ]
        
        for i, drone in enumerate(drones):
            # Skip landed drones
            if (hasattr(drone, 'has_landed') and drone.has_landed) or not drone.alive or not hasattr(drone, 'current_path') or not drone.current_path:
                continue
            
            color = colors[i % len(colors)]
            painter.setPen(color)
            painter.setBrush(color)
            
            # Draw path waypoints
            for j, waypoint in enumerate(drone.current_path):
                x, y = waypoint
                adjusted_y = y + offset_y
                
                # Different marker for current waypoint
                if j == drone.current_waypoint_index:
                    painter.drawEllipse(x - 4, adjusted_y - 4, 8, 8)  # Larger circle
                else:
                    painter.drawEllipse(x - 2, adjusted_y - 2, 4, 4)  # Small circle
            
            # Draw lines connecting waypoints
            painter.setPen(QColor(color.red(), color.green(), color.blue(), 150))
            for j in range(len(drone.current_path) - 1):
                x1, y1 = drone.current_path[j]
                x2, y2 = drone.current_path[j + 1]
                painter.drawLine(x1, y1 + offset_y, x2, y2 + offset_y)
            
            # Draw line from drone to current waypoint
            if drone.current_waypoint_index < len(drone.current_path):
                wx, wy = drone.current_path[drone.current_waypoint_index]
                painter.setPen(QColor(color.red(), color.green(), color.blue(), 200))
                painter.drawLine(int(drone.x), int(drone.y) + offset_y, wx, wy + offset_y)

    def draw_drone_with_status(self, painter, drone, offset_y):
        """Draw drone with status icons - but skip landed drones"""
        # Don't draw landed drones
        if hasattr(drone, 'has_landed') and drone.has_landed:
            return
        
        draw_x, draw_y = int(drone.x), int(drone.y) + offset_y
        
        # Main drone circle
        if hasattr(drone, 'returning_to_base') and drone.returning_to_base:
            painter.setBrush(QColor(255, 165, 0))  # Orange for returning
        elif drone.has_attacked:
            painter.setBrush(QColor(150, 150, 150))  # Gray for completed mission
        else:
            painter.setBrush(QColor(0, 120, 215))  # Blue for active
        
        painter.drawEllipse(draw_x, draw_y, 20, 20)
        
        # Status icons around the drone
        self.draw_status_icons(painter, drone, draw_x, draw_y)
        
        # Missile count text
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(draw_x + 25, draw_y + 15, f"{drone.missiles_fired}/{drone.max_missiles}")

    def draw_status_icons(self, painter, drone, x, y):
        """Draw status icons around drone"""
        # Attack status icon (top-right)
        if drone.has_attacked:
            painter.setBrush(QColor(255, 0, 0))  # Red checkmark
            painter.drawEllipse(x + 15, y - 5, 8, 8)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 6, QFont.Bold))
            painter.drawText(x + 17, y + 1, "✓")
        
        # Pathfinding status icon (top-left)
        if hasattr(drone, 'current_path') and drone.current_path:
            painter.setBrush(QColor(0, 255, 0))  # Green for active pathfinding
            painter.drawEllipse(x - 5, y - 5, 8, 8)
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", 6, QFont.Bold))
            painter.drawText(x - 3, y + 1, "P")
        
        # Missile status icon (bottom-right)
        if hasattr(drone, 'missiles') and drone.missiles:
            active_missiles = len([m for m in drone.missiles if m['active']])
            if active_missiles > 0:
                painter.setBrush(QColor(255, 255, 0))  # Yellow for active missiles
                painter.drawEllipse(x + 15, y + 15, 8, 8)
                painter.setPen(QColor(0, 0, 0))
                painter.setFont(QFont("Arial", 6, QFont.Bold))
                painter.drawText(x + 17, y + 21, str(active_missiles))
        
        # Return to base icon (bottom-left)
        if hasattr(drone, 'returning_to_base') and drone.returning_to_base:
            painter.setBrush(QColor(128, 0, 128))  # Purple for returning
            painter.drawEllipse(x - 5, y + 15, 8, 8)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 6, QFont.Bold))
            painter.drawText(x - 3, y + 21, "H")  # H for Home
        
        # Stuck indicator (center-top)
        if hasattr(drone, 'stuck_timer') and drone.stuck_timer > 50:
            painter.setBrush(QColor(255, 165, 0))  # Orange warning
            painter.drawEllipse(x + 6, y - 8, 8, 8)
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", 6, QFont.Bold))
            painter.drawText(x + 8, y - 2, "!")

    def draw_static_elements(self, painter, offset_y, obstacles, target, base):
        """Draw obstacles, target, and base"""
        # Draw obstacles first
        painter.setBrush(QColor(200, 50, 50))
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        
        for obs in obstacles:
            if not obs.is_hidden:
                if hasattr(obs, 'rect'):
                    adjusted = QRect(obs.rect.x(), obs.rect.y() + offset_y, obs.rect.width(), obs.rect.height())
                else:
                    adjusted = QRect(obs.x(), obs.y() + offset_y, obs.width(), obs.height())
                painter.drawRect(adjusted)

        # Helper function to check if a target should be drawn
        def should_draw_target(t):
            """Check if target should be visible based on mode and spotted status"""
            
            # CHECK IF TARGET WAS SPOTTED BY RADAR (highest priority)
            if hasattr(t, 'spotted_by_radar') and t.spotted_by_radar:
                return True
            
            # Check mode handler preference
            if hasattr(self, 'sim_modes') and self.sim_modes:
                mode_allows = self.sim_modes.get_current_handler().should_show_target()
                if mode_allows:
                    return True
            else:
                print("DEBUG: No sim_modes available")
            
            # Check if target is specifically hidden (and not spotted)
            hidden_status = getattr(t, 'hidden', False)
            spotted_status = getattr(t, 'spotted_by_radar', False)
            
            if hidden_status and not spotted_status:
                return False
            
            return True  # Default to showing target

        # Handle both single target and list of targets
        targets_to_draw = []
        if target is not None:
            try:
                # Check if iterable (multiple targets)
                iter(target)
                if isinstance(target, str):
                    targets_to_draw = [target]
                else:
                    targets_to_draw = list(target)
            except TypeError:
                # Single target
                targets_to_draw = [target]
        else:
            print("DEBUG: Target is None")
        # Draw all valid targets
        for i, single_target in enumerate(targets_to_draw):
            
            if not should_draw_target(single_target):
                continue  # Skip hidden targets
            
            
            # Draw the target with different colors based on status
            if getattr(single_target, 'spotted_by_radar', False):
                # Spotted target - keep it green but with a slight highlight
                painter.setBrush(QColor(50, 255, 50))  # Brighter green for spotted target
                painter.setPen(QPen(QColor(255, 255, 0), 2))  # Yellow border for spotted
            else:
                # Normal target - regular green
                painter.setBrush(QColor(50, 200, 50))  # Regular green for target
                painter.setPen(QPen(QColor(0, 0, 0), 2))    # Black border
            
            # Handle different position formats
            if hasattr(single_target, 'position') and hasattr(single_target, 'width') and hasattr(single_target, 'height'):
                target_adj = QRect(
                    int(single_target.position[0]), 
                    int(single_target.position[1]) + offset_y, 
                    single_target.width, 
                    single_target.height
                )
            elif hasattr(single_target, 'x') and hasattr(single_target, 'y'):
                target_adj = QRect(
                    single_target.x(), 
                    single_target.y() + offset_y, 
                    getattr(single_target, 'width', 30), 
                    getattr(single_target, 'height', 30)
                )
            else:
                continue  # Skip if we can't determine position
            
            painter.drawRect(target_adj)
            
            # Check if target is destroyed and add destroyed visual
            if hasattr(single_target, 'destroyed') and single_target.destroyed:
                # Draw "DESTROYED" text above target
                painter.setPen(QPen(QColor(255, 0, 0), 2))
                painter.setFont(QFont("Arial", 12, QFont.Bold))
                painter.drawText(
                    target_adj.x() - 10, 
                    target_adj.y() - 10, 
                    "DESTROYED"
                )
                
                # Draw X over destroyed target
                painter.setPen(QPen(QColor(255, 0, 0), 4))
                painter.drawLine(
                    target_adj.topLeft(), 
                    target_adj.bottomRight()
                )
                painter.drawLine(
                    target_adj.topRight(), 
                    target_adj.bottomLeft()
                )
                
                # Make target semi-transparent
                painter.setBrush(QColor(100, 100, 100, 128))
                painter.drawRect(target_adj)
            

        # Draw base (always visible)
        painter.setBrush(QColor(0, 0, 0))
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        base_adj = QRect(base.x(), base.y() + offset_y, base.width(), base.height())
        painter.drawRect(base_adj)

    def draw_missiles(self, painter, offset_y, drones):
        """Draw all missiles"""
        painter.setBrush(QColor(255, 0, 0))
        for drone in drones:
            for missile in getattr(drone, 'missiles', []):
                if missile['active']:
                    mx = int(round(missile['position'][0]))
                    my = int(round(missile['position'][1])) + offset_y
                    painter.drawEllipse(mx - 3, my - 3, 6, 6)

class RingExplosion:
    def __init__(self, x, y, max_radius=80):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = max_radius
        self.active = True
        self.age = 0
        self.max_age = 1.0
        
    def update(self, dt):
        self.age += dt
        progress = self.age / self.max_age
        
        if progress >= 1.0:
            self.active = False
            return False
        
        # Expanding ring with easing
        self.radius = self.max_radius * (1 - (1 - progress) ** 2)
        return True
    
    def draw(self, painter, offset_y=0):
        if not self.active:
            return
        
        # Calculate alpha based on age
        alpha = int(255 * (1 - self.age / self.max_age))
        
        # Draw multiple rings for effect
        for i in range(3):
            ring_radius = self.radius - i * 10
            if ring_radius > 0:
                color = QColor(255, 100 - i * 20, 0, max(0, alpha - i * 50))
                painter.setPen(QPen(color, 3))
                painter.setBrush(QBrush(Qt.transparent))
                painter.drawEllipse(
                    int(self.x - ring_radius),
                    int(self.y - ring_radius + offset_y),
                    int(ring_radius * 2),
                    int(ring_radius * 2)
                )