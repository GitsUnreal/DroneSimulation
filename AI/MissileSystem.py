import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple

class MissileType(Enum):
    STANDARD = "standard"
    HOMING = "homing"
    EXPLOSIVE = "explosive"
    PIERCING = "piercing"

class MissileState(Enum):
    LAUNCHING = "launching"
    FLYING = "flying"
    HOMING = "homing"
    EXPLODING = "exploding"
    DESTROYED = "destroyed"

@dataclass
class MissileConfig:
    speed: float = 20.0
    max_range: float = 500.0
    damage: int = 100
    explosion_radius: float = 30.0
    homing_range: float = 100.0
    fuel: float = 100.0
    maneuverability: float = 1.0

class Missile:
    def __init__(self, missile_id: str, drone_id: int, missile_type: MissileType, 
                 start_pos: Tuple[float, float], target_pos: Tuple[float, float],
                 config: MissileConfig = None):
        self.missile_id = missile_id
        self.drone_id = drone_id
        self.missile_type = missile_type
        self.state = MissileState.LAUNCHING
        
        # Position and movement
        self.position = np.array(start_pos, dtype=float)
        self.target_position = np.array(target_pos, dtype=float)
        self.velocity = np.zeros(2)
        self.path: List[Tuple[float, float]] = []
        self.path_index = 0
        
        # Configuration
        self.config = config or MissileConfig()
        self.fuel = self.config.fuel
        self.distance_traveled = 0.0
        
        # Tracking
        self.active = True
        self.age = 0
        self.last_position = self.position.copy()
        
        # Effects
        self.trail_points: List[Tuple[float, float]] = []
        self.explosion_timer = 0
        
        # Add callback support
        self.on_target_hit = None
        self.target_object = None

    def update(self, dt: float, drones: List, obstacles: List) -> bool:
        """Update missile state and return True if still active"""
        if not self.active:
            return False
            
        self.age += dt
        self.fuel -= dt * 10  # Fuel consumption
        
        # Check fuel depletion
        if self.fuel <= 0:
            self.explode()
            return False
            
        # Update based on state
        if self.state == MissileState.LAUNCHING:
            self._update_launching(dt)
        elif self.state == MissileState.FLYING:
            self._update_flying(dt, drones, obstacles)
        elif self.state == MissileState.HOMING:
            self._update_homing(dt, drones)
        elif self.state == MissileState.EXPLODING:
            self._update_explosion(dt)
            
        # Update trail
        self._update_trail()
        
        return self.active

    def _update_launching(self, dt: float):
        """Handle missile launch phase"""
        if self.age > 0.1:  # Short launch delay
            self.state = MissileState.FLYING
            self._calculate_initial_velocity()

    def _update_flying(self, dt: float, drones: List, obstacles: List):
        """Handle normal flight with pathfinding"""
        # Follow path if available
        if self.path and self.path_index < len(self.path):
            target = np.array(self.path[self.path_index])
            direction = target - self.position
            distance = np.linalg.norm(direction)
            
            if distance < 10:  # Reached waypoint
                self.path_index += 1
                if self.path_index >= len(self.path):
                    self.state = MissileState.HOMING
            else:
                self.velocity = (direction / distance) * self.config.speed
        else:
            # Direct flight to target
            direction = self.target_position - self.position
            distance = np.linalg.norm(direction)
            
            if distance < 15:  # Increased hit radius for better detection
                print(f"Missile {self.missile_id} hit target at distance {distance:.1f}")
                self.explode()
                return
            elif distance < self.config.homing_range and self.missile_type == MissileType.HOMING:
                self.state = MissileState.HOMING
            else:
                self.velocity = (direction / distance) * self.config.speed
        
        # Apply movement
        self._apply_movement(dt)
        
        # Check collisions with obstacles
        self._check_collisions(obstacles)
        
        # Check collision with actual target object (if provided)
        self._check_target_collision()

    def _update_homing(self, dt: float, drones: List):
        """Handle homing behavior"""
        # Find closest target
        closest_target = self._find_closest_target(drones)
        
        if closest_target:
            direction = closest_target - self.position
            distance = np.linalg.norm(direction)
            
            if distance < 5:
                self.explode()
                return
            
            # Homing guidance
            desired_velocity = (direction / distance) * self.config.speed
            steering = (desired_velocity - self.velocity) * self.config.maneuverability
            self.velocity += steering * dt
            
            # Limit speed
            speed = np.linalg.norm(self.velocity)
            if speed > self.config.speed:
                self.velocity = (self.velocity / speed) * self.config.speed
        
        self._apply_movement(dt)

    def _update_explosion(self, dt: float):
        """Handle explosion animation"""
        self.explosion_timer += dt
        if self.explosion_timer > 1.0:  # Explosion duration
            self.active = False

    def _apply_movement(self, dt: float):
        """Apply velocity to position"""
        self.last_position = self.position.copy()
        self.position += self.velocity * dt
        self.distance_traveled += np.linalg.norm(self.velocity * dt)
        
        # Check range limit
        if self.distance_traveled > self.config.max_range:
            self.explode()

    def _check_collisions(self, obstacles: List) -> bool:
        """Check collision with obstacles"""
        for obstacle in obstacles:
            if hasattr(obstacle, 'contains') and obstacle.contains(int(self.position[0]), int(self.position[1])):
                self.explode()
                return True
        return False

    def _find_closest_target(self, drones: List) -> Optional[np.ndarray]:
        """Find closest valid target for homing"""
        closest_dist = float('inf')
        closest_pos = None
        
        for drone in drones:
            if drone.drone_id != self.drone_id and drone.alive:
                dist = np.linalg.norm(drone.position - self.position)
                if dist < closest_dist and dist < self.config.homing_range:
                    closest_dist = dist
                    closest_pos = drone.position
        
        return closest_pos

    def _update_trail(self):
        """Update missile trail for visual effects"""
        self.trail_points.append((self.position[0], self.position[1]))
        
        # Limit trail length
        if len(self.trail_points) > 20:
            self.trail_points.pop(0)

    def _calculate_initial_velocity(self):
        """Calculate initial velocity based on target"""
        direction = self.target_position - self.position
        distance = np.linalg.norm(direction)
        if distance > 0:
            self.velocity = (direction / distance) * self.config.speed

    def explode(self):
        """Trigger missile explosion"""
        self.state = MissileState.EXPLODING
        self.explosion_timer = 0
        
        # Call hit callback if target was hit
        if self.on_target_hit and hasattr(self, 'hit_target') and self.hit_target:
            self.on_target_hit(self)
        
        print(f"Missile {self.missile_id} exploded at {self.position}")

    def get_explosion_effect(self) -> dict:
        """Get explosion effect data for rendering"""
        if self.state == MissileState.EXPLODING:
            progress = min(self.explosion_timer / 1.0, 1.0)
            return {
                'position': self.position,
                'radius': self.config.explosion_radius * progress,
                'intensity': 1.0 - progress,
                'active': True
            }
        return {'active': False}

    def _check_target_collision(self) -> bool:
        """Check if missile hit the target"""
        # Check distance to target position
        distance_to_target = np.linalg.norm(self.target_position - self.position)
        
        if distance_to_target < 20:  # Hit radius
            print(f"🎯 Missile {self.missile_id} HIT TARGET! Distance: {distance_to_target:.1f}")
            self.hit_target = True  # Mark that we hit the target
            self.explode()
            return True
        
        return False