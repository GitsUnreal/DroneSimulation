import numpy as np
from enum import Enum
from DroneSystem.Missiles.MissileSystem import MissileType
from dataclasses import dataclass

@dataclass
class DroneMovementConfig:
    """Configuration for drone movement parameters"""
    velocity: float = 5.0
    turn_rate: float = 0.1
    detection_range: float = 50.0
    attack_range: float = 30.0
    separation_weight: float = 2.0
    alignment_weight: float = 0.1
    cohesion_weight: float = 0.1
    target_weight: float = 1.5

class DroneMovementMode(Enum):
    """Different movement modes with predefined configs"""
    STANDARD = DroneMovementConfig(velocity=5.0, turn_rate=0.1)
    FAST_ASSAULT = DroneMovementConfig(velocity=15.0, turn_rate=0.15, attack_range=40.0)
    STEALTH = DroneMovementConfig(velocity=3.0, turn_rate=0.05, detection_range=75.0)
    PATROL = DroneMovementConfig(velocity=4.0, turn_rate=0.08, detection_range=60.0)
    SEARCH_RESCUE = DroneMovementConfig(velocity=6.0, turn_rate=0.12, detection_range=80.0)

class Drone:
    def __init__(self, position, velocity, drone_id):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.alive = True
        self.drone_id = drone_id
        self.has_attacked = False
        self.has_landed = False

        self.state = "idle"  # or "search", "attack", etc.

        # Default configurations
        self.movement_config = DroneMovementConfig()
        self.missile_config = None
        self.preferred_missile_type = MissileType.STANDARD
        
        self.max_missiles = 2
        self.missiles_fired = 0
        self.current_path = []
        self.current_waypoint_index = 0
        
        self.sync_from_position()

    def apply_movement_config(self, config: DroneMovementConfig):
        """Apply movement configuration to drone"""
        self.movement_config = config
        if hasattr(self, 'detection_range'):
            self.detection_range = config.detection_range
        if hasattr(self, 'attack_range'):
            self.attack_range = config.attack_range

    def get_current_speed(self):
        """Get current movement speed based on config"""
        return self.movement_config.velocity

    def get_turn_rate(self):
        """Get current turn rate based on config"""
        return self.movement_config.turn_rate

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
            #print(f"Drone {self.drone_id}: Cannot fire missile ({self.missiles_fired}/{self.max_missiles})")
            return

        start = tuple(self.position)
        target_pos = (target.position[0], target.position[1])

        # Create missile and fire
        guiding_missile = MissileType.HOMING(drone, target, oai, grid)
        if guiding_missile.shoot_missile(start, target_pos):
            self.missiles_fired += 1
            #print(f"Drone {self.drone_id}: Fired missile ({self.missiles_fired}/{self.max_missiles})")

    def attack_with_missile_system(self, target, missile_manager, missile_type=MissileType.STANDARD):
        """Enhanced attack method using new missile system"""
        if not self.can_fire_missile():
            #print(f"Drone {self.drone_id}: Cannot fire missile ({self.missiles_fired}/{self.max_missiles})")
            return False

        target_pos = (target.position[0], target.position[1])
        
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
        #print(f"Drone {self.drone_id} has successfully landed at base")

    def reactivate_from_base(self, new_target_pos=None):
        """Reactivate a landed drone for a new mission"""
        if not hasattr(self, 'has_landed') or not self.has_landed:
            #print(f"Drone {self.drone_id} is not landed, cannot reactivate")
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
        
        #print(f"Drone {self.drone_id} reactivated for new mission")
        return True

    def get_center_position(self):
        """Get the center position of the drone"""
        size = getattr(self, 'size', 20)  # Default drone size
        return (
            self.position[0] + size / 2,
            self.position[1] + size / 2
        )

    def get_missile_spawn_position(self):
        """Get alternating spawn position above/below drone"""
        size = getattr(self, 'size', 20)
        offset = 5
        # Alternate above/below based on missiles fired
        if self.missiles_fired % 2 == 0:
            # Above
            return (self.position[0] + size / 2, self.position[1] - offset)
        else:
            # Below
            return (self.position[0] + size / 2, self.position[1] + size + offset)
