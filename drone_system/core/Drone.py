from core.entities.base.MovableEntity import MovableEntity
from config.DroneConfig import DroneConfig
import numpy as np
from enum import Enum
from drone_system.weapons.MissileSystem import MissileType
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

class Drone(MovableEntity):
    """Simplified drone class with core functionality"""
    
    def __init__(self, position, velocity, drone_id):
        super().__init__(position, velocity, drone_id)
        self.has_attacked = False
        self.has_landed = False
        self.missiles_fired = 0
        self.max_missiles = DroneConfig.MAX_MISSILES
        
        # Navigation
        self.current_path = []
        self.current_waypoint_index = 0
        
        # Sync position coordinates
        self._sync_coordinates()
        self.target_found = False
    
    def _sync_coordinates(self):
        """Sync x, y with position array"""
        self.x, self.y = self.position
    
    def update(self, dt):
        """Update drone state"""
        self.position += self.velocity * dt
        self.constrain_to_bounds()
        self._sync_coordinates()
    
    def can_fire_missile(self):
        """Check if drone can fire another missile"""
        return self.missiles_fired < self.max_missiles
    
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

    def land_at_base(self):
        """Land drone at base"""
        self.has_landed = True
        self.velocity = np.zeros(2)
    
    def is_active(self):
        """Check if drone is actively participating"""
        return self.alive and not self.has_landed

def get_landed_drones_at_base(drones):
    """Get all drones that are landed at base"""
    return [drone for drone in drones if hasattr(drone, 'has_landed') and drone.has_landed]
    @property
    def x(self):
        """Get x position"""
        return self.position[0] if hasattr(self, 'position') else 100
    
    @x.setter
    def x(self, value):
        """Set x position"""
        if hasattr(self, 'position'):
            self.position[0] = value
    
    @property
    def y(self):
        """Get y position"""
        return self.position[1] if hasattr(self, 'position') else 100
    
    @y.setter
    def y(self, value):
        """Set y position"""
        if hasattr(self, 'position'):
            self.position[1] = value