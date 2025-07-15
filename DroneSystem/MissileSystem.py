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
    missile_type: MissileType = MissileType.STANDARD

class MissileConfigPresets(Enum):
    """Predefined missile configurations for different types"""
    STANDARD = MissileConfig(
        speed=20.0, damage=100, explosion_radius=30.0, 
        missile_type=MissileType.STANDARD
    )
    EXPLOSIVE = MissileConfig(
        speed=15.0, damage=150, explosion_radius=50.0, 
        missile_type=MissileType.EXPLOSIVE
    )
    HOMING = MissileConfig(
        speed=100.0, damage=80, homing_range=150.0, maneuverability=1.5,
        missile_type=MissileType.HOMING
    )
    PIERCING = MissileConfig(
        speed=30.0, damage=120, explosion_radius=15.0,
        missile_type=MissileType.PIERCING
    )

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
        if not self.active:
            return False

        self.age += dt
        self.fuel -= dt * 10

        if self.fuel <= 0:
            self.explode()
            return False

        # Handle state transitions
        if self.state == MissileState.LAUNCHING:
            self._update_launching(dt)
        elif self.state == MissileState.FLYING:
            self._update_flying(dt, drones, obstacles)
        elif self.state == MissileState.HOMING:
            self._update_homing(dt, drones)
        elif self.state == MissileState.EXPLODING:
            self._update_explosion(dt)
        # DESTROYED state does nothing

        self._update_trail()
        return self.active

    def _update_standard(self, dt, drones, obstacles):
        # Straight flight to target center
        target_center = self._get_target_center()
        direction = target_center - self.position
        if np.linalg.norm(direction) > 1:
            self.velocity = (direction / np.linalg.norm(direction)) * self.config.speed
        self._apply_movement(dt)
        self._check_collisions(obstacles)
        self._check_target_collision()

    def _update_explosive(self, dt, drones, obstacles):
        # Slower, larger explosion radius, straight flight
        target_center = self._get_target_center()
        direction = target_center - self.position
        if np.linalg.norm(direction) > 1:
            self.velocity = (direction / np.linalg.norm(direction)) * (self.config.speed * 0.7)
        self._apply_movement(dt)
        self._check_collisions(obstacles)
        self._check_target_collision()

    def _update_piercing(self, dt, drones, obstacles):
        # Fast, ignores obstacles, straight flight
        target_center = self._get_target_center()
        direction = target_center - self.position
        if np.linalg.norm(direction) > 1:
            self.velocity = (direction / np.linalg.norm(direction)) * (self.config.speed * 1.2)
        self._apply_movement(dt)
        self._check_target_collision()  # Ignores obstacles

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
            # Direct flight to target CENTER
            target_center = self._get_target_center()
            direction = target_center - self.position
            distance = np.linalg.norm(direction)
            
            if distance < 15:  # Increased hit radius for better detection
                #print(f"Missile {self.missile_id} hit target at distance {distance:.1f}")
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
        
        if closest_target is not None:
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
        
        #print(f"Missile {self.missile_id} exploded at {self.position}")

    def get_explosion_effect(self) -> dict:
        """Get explosion effect data for rendering"""
        if self.state == MissileState.EXPLODING:
            progress = min(self.explosion_timer / 1.0, 1.0)
            return {
                'position': self.position,
                'radius': self.config.explosion_radius * progress,
                'intensity': 1.0 - progress,
                'active': True,
                'max_radius': self.config.explosion_radius,  # Add max radius for scaling
                'missile_type': self.missile_type.value  # Add missile type for different effects
            }
        return {'active': False}

    def _check_target_collision(self) -> bool:
        """Check if missile hit the target"""
        # Get target center position
        target_center = self._get_target_center()
        
        # Check distance to target center
        distance_to_target = np.linalg.norm(target_center - self.position)
        
        # Use a reasonable hit radius - smaller for more precision
        hit_radius = 20  # Reduced from 20 for better precision
        
        if distance_to_target < hit_radius:
            #print(f"🎯 Missile {self.missile_id} HIT TARGET! Distance: {distance_to_target:.1f}")
            self.hit_target = True
            self.explode()
            return True
        
        return False

    def _get_target_center(self) -> np.ndarray:
        """Get the center position of the target"""
        if self.target_object:
            # If we have a target object, calculate its center
            if hasattr(self.target_object, 'position') and hasattr(self.target_object, 'width') and hasattr(self.target_object, 'height'):
                return np.array([
                    self.target_object.position[0] + self.target_object.width / 2,
                    self.target_object.position[1] + self.target_object.height / 2
                ])
            elif hasattr(self.target_object, 'x') and hasattr(self.target_object, 'y'):
                width = getattr(self.target_object, 'width', 30)
                height = getattr(self.target_object, 'height', 30)
                return np.array([
                    self.target_object.x() + width / 2,
                    self.target_object.y() + height / 2
                ])
        
        # Fallback to stored target position
        return self.target_position