import numpy as np
import random
import math

class target:
    def __init__(self, target_id, position, height=20, width=20, is_moving_target=False, is_convoy_target=False, hidden=False):
        """
        Initialize a target with an ID, position, height, and width.
        """
        self.target_id = target_id
        self.position = np.array(position, dtype=float)  # Convert to numpy array
        self.destroyed = False
        self.height = height
        self.width = width

        self.hidden = hidden
        self.is_moving_target = is_moving_target
        self.is_convoy_target = is_convoy_target
        
        # Movement properties
        self.velocity = np.zeros(2)
        self.speed = 2.0  # Base movement speed
        self.direction = np.array([1.0, 0.0])  # Initial direction
        
        # Random path properties
        self.waypoints = []
        self.current_waypoint_index = 0
        self.path_complete = False
        
        # Boundary constraints
        self.bounds = {'min_x': 50, 'max_x': 800, 'min_y': 100, 'max_y': 500}
        
        # Movement patterns
        self.movement_pattern = "none"  # "linear", "circular", "waypoint", "random", "none"
        self.pattern_timer = 0
        self.direction_change_interval = 3.0  # seconds

    def set_none_movement(self):
        """Set target to not move"""
        self.movement_pattern = "none"
        self.velocity = np.zeros(2)
        self.direction = np.zeros(2)
        self.speed = 0.0
        self.pattern_timer = 0

    def set_linear_movement(self, direction, speed=2.0):
        """Set target to move in a straight line"""
        self.movement_pattern = "linear"
        self.direction = np.array(direction, dtype=float)
        self.direction = self.direction / np.linalg.norm(self.direction)  # Normalize
        self.speed = speed
        self.velocity = self.direction * self.speed

    def set_circular_movement(self, center, radius, angular_speed=0.02):
        """Set target to move in a circle"""
        self.movement_pattern = "circular"
        self.circle_center = np.array(center, dtype=float)
        self.circle_radius = radius
        self.angular_speed = angular_speed
        self.angle = 0

    def set_random_path(self, num_waypoints=5, bounds=None):
        """Generate random waypoints for the target to follow"""
        self.movement_pattern = "waypoint"
        if bounds:
            self.bounds = bounds
        
        self.waypoints = []
        for _ in range(num_waypoints):
            x = random.randint(self.bounds['min_x'], self.bounds['max_x'])
            y = random.randint(self.bounds['min_y'], self.bounds['max_y'])
            self.waypoints.append(np.array([x, y], dtype=float))
        
        self.current_waypoint_index = 0
        self.path_complete = False
        #print(f"Target {self.target_id} waypoints: {self.waypoints}")

    def set_random_movement(self, direction_change_interval=3.0, speed=2.0):
        """Set target to move in random directions"""
        self.movement_pattern = "random"
        self.direction_change_interval = direction_change_interval
        self.speed = speed
        self._generate_random_direction()

    def _generate_random_direction(self):
        """Generate a new random direction"""
        angle = random.uniform(0, 2 * math.pi)
        self.direction = np.array([math.cos(angle), math.sin(angle)])
        self.velocity = self.direction * self.speed

    def update_movement(self, dt=0.05):
        """Update target position based on movement pattern"""
        if self.destroyed or not self.is_moving_target:
            return
        
        self.pattern_timer += dt
        
        if self.movement_pattern == "linear":
            self._update_linear_movement()
        elif self.movement_pattern == "circular":
            self._update_circular_movement(dt)
        elif self.movement_pattern == "waypoint":
            self._update_waypoint_movement()
        elif self.movement_pattern == "random":
            self._update_random_movement()
        else:
            self.set_none_movement()
        
        # Keep target within bounds
        self._constrain_to_bounds()

    def _update_linear_movement(self):
        """Update position for linear movement"""
        new_position = self.position + self.velocity * 0.05
        
        # Bounce off boundaries
        if new_position[0] <= self.bounds['min_x'] or new_position[0] >= self.bounds['max_x']:
            self.direction[0] *= -1
            self.velocity = self.direction * self.speed
        if new_position[1] <= self.bounds['min_y'] or new_position[1] >= self.bounds['max_y']:
            self.direction[1] *= -1
            self.velocity = self.direction * self.speed
        
        self.position += self.velocity * 0.05

    def _update_circular_movement(self, dt):
        """Update position for circular movement"""
        self.angle += self.angular_speed
        
        self.position[0] = self.circle_center[0] + self.circle_radius * math.cos(self.angle)
        self.position[1] = self.circle_center[1] + self.circle_radius * math.sin(self.angle)

    def _update_waypoint_movement(self):
        """Update position for waypoint-based movement"""
        if self.path_complete or not self.waypoints:
            return
        
        current_waypoint = self.waypoints[self.current_waypoint_index]
        direction = current_waypoint - self.position
        distance = np.linalg.norm(direction)
        
        if distance < 10:  # Reached waypoint
            self.current_waypoint_index += 1
            if self.current_waypoint_index >= len(self.waypoints):
                self.path_complete = True
                #print(f"Target {self.target_id} completed waypoint path")
                # Optionally loop back to start
                # self.current_waypoint_index = 0
        else:
            # Move towards current waypoint
            direction = direction / distance  # Normalize
            self.velocity = direction * self.speed
            self.position += self.velocity * 0.05

    def _update_random_movement(self):
        """Update position for random movement"""
        # Change direction periodically
        if self.pattern_timer >= self.direction_change_interval:
            self._generate_random_direction()
            self.pattern_timer = 0
        
        # Move in current direction
        self.position += self.velocity * 0.05

    def _constrain_to_bounds(self):
        """Keep target within specified bounds"""
        self.position[0] = max(self.bounds['min_x'], min(self.bounds['max_x'], self.position[0]))
        self.position[1] = max(self.bounds['min_y'], min(self.bounds['max_y'], self.position[1]))

    def get_predicted_position(self, time_ahead=1.0):
        """Predict where target will be in the future"""
        if not self.is_moving_target or self.destroyed:
            return self.position
        
        if self.movement_pattern == "linear":
            return self.position + self.velocity * time_ahead
        elif self.movement_pattern == "circular":
            future_angle = self.angle + self.angular_speed * time_ahead * 20  # Adjust multiplier
            pred_x = self.circle_center[0] + self.circle_radius * math.cos(future_angle)
            pred_y = self.circle_center[1] + self.circle_radius * math.sin(future_angle)
            return np.array([pred_x, pred_y])
        else:
            return self.position + self.velocity * time_ahead

    def destroy(self):
        self.destroyed = True
        #print(f"Target {self.target_id} at {self.position} has been destroyed.")
    
    def is_destroyed(self):
        return self.destroyed

    def x(self):
        return int(self.position[0])
    
    def y(self):
        return int(self.position[1])