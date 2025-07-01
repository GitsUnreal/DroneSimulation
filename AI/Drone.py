import numpy as np
from AI.MissileSystem import MissileType

class Drone:
    def __init__(self, position, velocity, drone_id):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.alive = True
        self.drone_id = drone_id
        self.has_attacked = False
        self.has_landed = False

        self.max_missiles = 2
        self.missiles_fired = 0
        self.current_path = []
        self.current_waypoint_index = 0
        
        
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

    def attack_with_missile_system(self, target, missile_manager, missile_type=MissileType.STANDARD):
        """Enhanced attack method using new missile system"""
        if not self.can_fire_missile():
            print(f"Drone {self.drone_id}: Cannot fire missile ({self.missiles_fired}/{self.max_missiles})")
            return False

        target_pos = (target.x(), target.y())
        
        # Choose missile type based on distance or drone state
        if hasattr(self, 'missile_preference'):
            missile_type = self.missile_preference
        
        success = missile_manager.fire_missile(self, target_pos, missile_type)
        
        if success:
            print(f"Drone {self.drone_id}: Fired {missile_type.value} missile ({self.missiles_fired}/{self.max_missiles})")
        
        return success

    def reset_missiles(self):
        """Reset missile count and clear missiles."""
        # Only reset missiles list, not the fired count for mission tracking
        if hasattr(self, 'missiles'):
            self.missiles.clear()
        if hasattr(self, 'returning_to_base'):
            del self.returning_to_base
        # Don't reset missiles_fired here to preserve mission statistics

    def is_active(self):
        """Check if drone is active in the simulation"""
        return self.alive and not self.has_landed

    def land_at_base(self):
        """Land drone at base (removes from active simulation)"""
        self.has_landed = True
        # Don't set alive = False, keep drone alive but landed
        print(f"Drone {self.drone_id} has successfully landed at base")

    def reactivate_from_base(self, new_target_pos=None):
        """Reactivate a landed drone for a new mission"""
        if not hasattr(self, 'has_landed') or not self.has_landed:
            print(f"Drone {self.drone_id} is not landed, cannot reactivate")
            return False
        
        # Reset drone state for new mission
        self.has_landed = False
        self.has_attacked = False
        self.missiles_fired = 0
        
        # Clear any existing paths
        self.current_path = []
        self.current_waypoint_index = 0
        
        # Clear missiles
        if hasattr(self, 'missiles'):
            self.missiles.clear()
        
        # Remove return to base flag
        if hasattr(self, 'returning_to_base'):
            delattr(self, 'returning_to_base')
        
        # Optionally move to new position (if provided)
        if new_target_pos:
            self.position = np.array(new_target_pos, dtype=float)
            self.sync_from_position()
        
        print(f"Drone {self.drone_id} reactivated for new mission")
        return True

def get_landed_drones_at_base(drones):
    """Get all drones that are landed at base"""
    return [drone for drone in drones if hasattr(drone, 'has_landed') and drone.has_landed]
