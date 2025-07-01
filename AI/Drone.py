import numpy as np
from .GuidingMissile import GuidingMissile

class Drone:
    def __init__(self, position, velocity, drone_id):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.alive = True
        self.drone_id = drone_id
        self.has_attacked = False

        self.max_missiles = 3  # Increased from 2 to 3
        self.missiles_fired = 0
        self.current_path = []
        self.current_waypoint_index = 0
        
        # Sync position variables
        self.sync_from_position()

    def update_position_sync(self):
        """Update position array from x, y coordinates."""
        self.position[0], self.position[1] = self.x, self.y

    def sync_from_position(self):
        """Update x, y coordinates from position array."""
        self.x, self.y = self.position

    def constrain_to_bounds(self, width=1080, height=720):
        """Keep drone within screen bounds."""
        self.position[0] = max(10, min(self.position[0], width - 30))
        self.position[1] = max(10, min(self.position[1], height - 30))
        self.sync_from_position()

    def destroy(self):
        """Mark drone as destroyed."""
        self.alive = False

    def is_destroyed(self):
        """Check if drone is destroyed."""
        return not self.alive

    def can_fire_missile(self):
        """Check if drone can fire another missile."""
        return self.alive and self.missiles_fired < self.max_missiles

    def attack(self, drone, target, oai, grid):
        """Attack the target with a missile."""
        if not self.can_fire_missile():
            print(f"Drone {self.drone_id}: Cannot fire missile ({self.missiles_fired}/{self.max_missiles})")
            return

        start = tuple(self.position)
        target_pos = (target.x(), target.y())

        # Create missile and fire
        guiding_missile = GuidingMissile(drone, target, oai, grid)
        if guiding_missile.shoot_missile(start, target_pos):
            self.missiles_fired += 1
            print(f"Drone {self.drone_id}: Fired missile ({self.missiles_fired}/{self.max_missiles})")

    def reset_missiles(self):
        """Reset missile count and clear missiles."""
        self.missiles_fired = 0
        if hasattr(self, 'missiles'):
            self.missiles.clear()
        if hasattr(self, 'returning_to_base'):
            del self.returning_to_base
