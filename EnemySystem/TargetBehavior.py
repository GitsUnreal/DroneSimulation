import numpy as np
import random
import math

class TargetBehavior:
    def __init__(self, target):
        self.target = target

    def set_none_movement(self):
        self.target.movement_pattern = "none"
        self.target.velocity = np.zeros(2)
        self.target.direction = np.zeros(2)
        self.target.speed = 0.0
        self.target.pattern_timer = 0

    def set_linear_movement(self, direction, speed=2.0):
        self.target.movement_pattern = "linear"
        self.target.direction = np.array(direction, dtype=float)
        self.target.speed = speed
        self.target.velocity = self.target.direction * self.target.speed
        self.target.pattern_timer = 0

    def set_circular_movement(self, center, radius, angular_speed=0.05):
        self.target.movement_pattern = "circular"
        self.target.circular_center = np.array(center, dtype=float)
        self.target.circular_radius = radius
        self.target.angular_speed = angular_speed
        self.target.angle = 0.0
        self.target.pattern_timer = 0

    def set_waypoint_movement(self, waypoints, speed=2.0):
        self.target.movement_pattern = "waypoint"
        self.target.waypoints = [np.array(wp, dtype=float) for wp in waypoints]
        self.target.current_waypoint_index = 0
        self.target.speed = speed
        self.target.pattern_timer = 0

    def set_random_movement(self, speed=2.0):
        self.target.movement_pattern = "random"
        self.target.speed = speed
        self.target.pattern_timer = 0

    def update(self, dt=1.0):
        # Call this in the main update loop to update target position
        pattern = self.target.movement_pattern
        if pattern == "none":
            return
        elif pattern == "linear":
            self.target.position += self.target.direction * self.target.speed * dt
        elif pattern == "circular":
            self.target.angle += self.target.angular_speed * dt
            x = self.target.circular_center[0] + self.target.circular_radius * math.cos(self.target.angle)
            y = self.target.circular_center[1] + self.target.circular_radius * math.sin(self.target.angle)
            self.target.position = np.array([x, y], dtype=float)
        elif pattern == "waypoint":
            if self.target.waypoints:
                wp = self.target.waypoints[self.target.current_waypoint_index]
                direction = wp - self.target.position
                dist = np.linalg.norm(direction)
                if dist < 5:
                    self.target.current_waypoint_index = (self.target.current_waypoint_index + 1) % len(self.target.waypoints)
                else:
                    direction = direction / (dist + 1e-6)
                    self.target.position += direction * self.target.speed * dt
        elif pattern == "random":
            # Random walk or change direction at intervals
            self.target.pattern_timer += dt
            if self.target.pattern_timer > self.target.direction_change_interval:
                angle = random.uniform(0, 2 * math.pi)
                self.target.direction = np.array([math.cos(angle), math.sin(angle)])
                self.target.pattern_timer = 0
            self.target.position += self.target.direction * self.target.speed * dt
        # Clamp to bounds if needed
        if hasattr(self.target, 'bounds'):
            b = self.target.bounds
            self.target.position[0] = np.clip(self.target.position[0], b['min_x'], b['max_x'])
            self.target.position[1] = np.clip(self.target.position[1], b['min_y'], b['max_y'])
