import numpy as np
import random

class AntiDroneBehavior:
    def __init__(self, antidrone):
        self.antidrone = antidrone

    def set_patrol(self, waypoints, speed=2.0):
        self.antidrone.movement_pattern = "patrol"
        self.antidrone.waypoints = [np.array(wp, dtype=float) for wp in waypoints]
        self.antidrone.current_waypoint_index = 0
        self.antidrone.speed = speed

    def set_random_patrol(self, speed=2.0):
        self.antidrone.movement_pattern = "random"
        self.antidrone.speed = speed
        self.antidrone.pattern_timer = 0

    def update(self, dt=1.0):
        pattern = getattr(self.antidrone, 'movement_pattern', 'none')
        if pattern == "patrol" and hasattr(self.antidrone, 'waypoints'):
            wp = self.antidrone.waypoints[self.antidrone.current_waypoint_index]
            direction = wp - self.antidrone.position
            dist = np.linalg.norm(direction)
            if dist < 5:
                self.antidrone.current_waypoint_index = (self.antidrone.current_waypoint_index + 1) % len(self.antidrone.waypoints)
            else:
                direction = direction / (dist + 1e-6)
                self.antidrone.position += direction * self.antidrone.speed * dt
        elif pattern == "random":
            self.antidrone.pattern_timer += dt
            if self.antidrone.pattern_timer > 3.0:
                angle = random.uniform(0, 2 * np.pi)
                self.antidrone.direction = np.array([np.cos(angle), np.sin(angle)])
                self.antidrone.pattern_timer = 0
            self.antidrone.position += self.antidrone.direction * self.antidrone.speed * dt
        # Clamp to bounds if needed
        if hasattr(self.antidrone, 'bounds'):
            b = self.antidrone.bounds
            self.antidrone.position[0] = np.clip(self.antidrone.position[0], b['min_x'], b['max_x'])
            self.antidrone.position[1] = np.clip(self.antidrone.position[1], b['min_y'], b['max_y'])
