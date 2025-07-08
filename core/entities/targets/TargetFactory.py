"""Factory for creating different types of targets"""
from .Target import Target
import random

class TargetFactory:
    """Factory for creating targets"""
    
    @staticmethod
    def create_random_target(obstacles=None, bounds=None):
        """Create a random target avoiding obstacles"""
        # Default bounds if not provided
        if bounds is None:
            bounds = (100, 100, 600, 400)  # x, y, width, height
        
        # If obstacles is actually a bounds tuple (backward compatibility)
        if obstacles is not None and isinstance(obstacles, (tuple, list)) and len(obstacles) == 4:
            if all(isinstance(x, (int, float)) for x in obstacles):
                bounds = obstacles
                obstacles = None
        
        max_attempts = 50
        for attempt in range(max_attempts):
            # Generate random position within bounds
            x = random.randint(bounds[0], bounds[0] + bounds[2] - 30)
            y = random.randint(bounds[1], bounds[1] + bounds[3] - 30)
            
            # Check if position conflicts with obstacles
            position_valid = True
            if obstacles:
                for obstacle in obstacles:
                    if hasattr(obstacle, 'x') and hasattr(obstacle, 'y'):
                        # Check if target would overlap with obstacle
                        obs_x, obs_y = obstacle.x(), obstacle.y()
                        obs_width = getattr(obstacle, 'width', lambda: 50)()
                        obs_height = getattr(obstacle, 'height', lambda: 50)()
                        
                        # Simple overlap check with 20px buffer
                        if (x < obs_x + obs_width + 20 and x + 30 > obs_x - 20 and
                            y < obs_y + obs_height + 20 and y + 30 > obs_y - 20):
                            position_valid = False
                            break
            
            if position_valid:
                return Target(
                    target_id=random.randint(1000, 9999),
                    position=(x, y),
                    height=30,
                    width=30
                )
        
        # Fallback: create target at default safe position
        print("⚠️  Could not find safe position for target, using default")
        return Target(
            target_id=random.randint(1000, 9999),
            position=(200, 200),
            height=30,
            width=30
        )
    
    @staticmethod
    def create_stationary_target(x, y, target_id=None):
        """Create a stationary target at specific position"""
        if target_id is None:
            target_id = random.randint(1000, 9999)
            
        return Target(
            target_id=target_id,
            position=(x, y),
            height=30,
            width=30,
            is_moving_target=False
        )
    
    @staticmethod
    def create_moving_target(x, y, target_id=None):
        """Create a moving target"""
        if target_id is None:
            target_id = random.randint(1000, 9999)
            
        target = Target(
            target_id=target_id,
            position=(x, y),
            height=30,
            width=30,
            is_moving_target=True
        )
        
        # Set random movement direction
        direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
        speed = random.uniform(1.0, 3.0)
        
        if hasattr(target, 'set_linear_movement'):
            target.set_linear_movement(direction, speed)
        
        return target
    
    @staticmethod
    def create_target_at_safe_distance(drones, obstacles=None, min_distance=100):
        """Create a target at safe distance from drones"""
        bounds = (100, 100, 600, 400)
        max_attempts = 100
        
        for attempt in range(max_attempts):
            target = TargetFactory.create_random_target(obstacles, bounds)
            
            # Check distance from all drones
            safe_position = True
            for drone in drones:
                if hasattr(drone, 'x') and hasattr(drone, 'y'):
                    distance = ((target.x() - drone.x)**2 + (target.y() - drone.y)**2)**0.5
                    if distance < min_distance:
                        safe_position = False
                        break
            
            if safe_position:
                return target
        
        # Fallback position far from typical drone spawn
        return TargetFactory.create_stationary_target(600, 400)