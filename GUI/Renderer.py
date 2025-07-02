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
            print(f"DEBUG: Checking should_draw_target for: {t}")
            
            # CHECK IF TARGET WAS SPOTTED BY RADAR (highest priority)
            if hasattr(t, 'spotted_by_radar') and t.spotted_by_radar:
                print("DEBUG: Target spotted by radar - showing despite being hidden")
                return True
            
            # Check mode handler preference
            if hasattr(self, 'sim_modes') and self.sim_modes:
                mode_allows = self.sim_modes.get_current_handler().should_show_target()
                print(f"DEBUG: Mode allows target: {mode_allows}")
                print(f"DEBUG: Current mode: {self.sim_modes.get_current_handler().name}")
                if mode_allows:
                    print("DEBUG: Mode says show target")
                    return True
            else:
                print("DEBUG: No sim_modes available")
            
            # Check if target is specifically hidden (and not spotted)
            hidden_status = getattr(t, 'hidden', False)
            spotted_status = getattr(t, 'spotted_by_radar', False)
            print(f"DEBUG: Target hidden: {hidden_status}, spotted: {spotted_status}")
            
            if hidden_status and not spotted_status:
                print("DEBUG: Target is hidden and not spotted")
                return False
            
            print("DEBUG: Target should be drawn")
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
                print(f"DEBUG: Target is iterable, targets_to_draw: {len(targets_to_draw)}")
            except TypeError:
                # Single target
                targets_to_draw = [target]
                print(f"DEBUG: Target is single, targets_to_draw: {len(targets_to_draw)}")
        else:
            print("DEBUG: Target is None")

        # Draw all valid targets
        for i, single_target in enumerate(targets_to_draw):
            print(f"DEBUG: Processing target {i}: {single_target}")
            
            if not should_draw_target(single_target):
                print(f"DEBUG: Skipping target {i} - should not draw")
                continue  # Skip hidden targets
            
            print(f"DEBUG: Drawing target {i}")
            
            # Draw the target with different colors based on status
            if getattr(single_target, 'spotted_by_radar', False):
                # Spotted target - use bright yellow/orange
                painter.setBrush(QColor(255, 215, 0))  # Gold for spotted target
                painter.setPen(QPen(QColor(255, 0, 0), 3))  # Red border for spotted
                
                # Add pulsing effect for newly spotted targets
                if not hasattr(single_target, 'spot_time'):
                    single_target.spot_time = 0
                single_target.spot_time += 1
                
                # Pulsing border for first few seconds after spotting
                if single_target.spot_time < 100:  # Pulse for ~5 seconds at 20fps
                    border_width = 3 + int(2 * abs(np.sin(single_target.spot_time * 0.3)))
                    painter.setPen(QPen(QColor(255, 0, 0), border_width))
            else:
                # Normal target (should rarely be seen in search and destroy)
                painter.setBrush(QColor(50, 200, 50))  # Green for normal target
                painter.setPen(QPen(QColor(0, 0, 0), 2))
            
            # Handle different position formats
            if hasattr(single_target, 'position') and hasattr(single_target, 'width') and hasattr(single_target, 'height'):
                print(f"DEBUG: Using position format: pos={single_target.position}, w={single_target.width}, h={single_target.height}")
                target_adj = QRect(
                    int(single_target.position[0]), 
                    int(single_target.position[1]) + offset_y, 
                    single_target.width, 
                    single_target.height
                )
            elif hasattr(single_target, 'x') and hasattr(single_target, 'y'):
                print(f"DEBUG: Using x/y format: x={single_target.x()}, y={single_target.y()}")
                target_adj = QRect(
                    single_target.x(), 
                    single_target.y() + offset_y, 
                    getattr(single_target, 'width', 30), 
                    getattr(single_target, 'height', 30)
                )
            else:
                print("DEBUG: Cannot determine target position format - skipping")
                continue  # Skip if we can't determine position
            
            print(f"DEBUG: Drawing target rect: {target_adj}")
            painter.drawRect(target_adj)
            
            # Add different labels based on status
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            
            if getattr(single_target, 'spotted_by_radar', False):
                painter.drawText(target_adj.center().x() - 8, target_adj.center().y() + 5, "🎯")  # Target emoji for spotted
            else:
                painter.drawText(target_adj.center().x() - 5, target_adj.center().y() + 5, "T")   # Regular T for unspotted
            
            print(f"DEBUG: Successfully drew target {i}")

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