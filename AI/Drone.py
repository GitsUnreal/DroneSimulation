import numpy as np
from .GuidingMissile import GuidingMissile

class Drone:
    def __init__(self, position, velocity, id):
        """
        Initialize a drone with position (x, y) and velocity (vx, vy).
        :param position: Initial position as [x, y] array.
        :param velocity: Initial velocity as [vx, vy] array.
        """

        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.x = float(self.position[0])
        self.y = float(self.position[1])
        self.alive = True
        self.id = id

        self.current_path = []
        self.current_waypoint_index = 0

    def update_position_sync(self):
        """Sync position array with x, y coordinates"""
        self.position[0] = self.x
        self.position[1] = self.y
    
    def sync_from_position(self):
        """Sync x, y coordinates from position array"""
        self.x = float(self.position[0])
        self.y = float(self.position[1])

    def constrain_to_bounds(self, width=1080, height=720):
        """Keep drone within screen boundaries"""
        self.position[0] = max(10, min(self.position[0], width - 30))
        self.position[1] = max(10, min(self.position[1], height - 30))
        self.sync_from_position()

    def move_towards_target(self, width, height, target):
        """
        Move the drone towards the target while avoiding going out of bounds.
        The drone will adjust its position based on its velocity and the target's position.
        :param width: Width of the area to keep the drone within.
        :param height: Height of the area to keep the drone within.
        :param target: The target QRect object that the drone is moving
        """
        if not self.alive:
            return

        # Move towards the target
        if self.x < target.x():
            self.x += self.velocity[0]
        elif self.x > target.x() + target.width():
            self.x -= self.velocity[0]
        if self.y < target.y():
            self.y += self.velocity[1]
        elif self.y > target.y() + target.height():
            self.y -= self.velocity[1]
        
        # Keep within bounds
        self.x = max(0, min(self.x, width - 20))
        self.y = max(0, min(self.y, height - 20))

    def move_to(self, x, y):
        """
        Move the drone to a specific position (x, y).
        :param x: New x-coordinate of the drone.
        :param y: New y-coordinate of the drone.
        """
        if not self.alive:
            return
        self.x = x
        self.y = y

    def destroy(self):
        """
        Mark the drone as destroyed.
        This will prevent it from moving or interacting with the environment.
        """
        self.alive = False

    def is_destroyed(self):
        """
        Check if the drone is destroyed.
        :return: True if the drone is destroyed, False otherwise.
        """
        return not self.alive
    
    def attack(self, drone, target, oai, grid):
        """
        Attack the target.
        This method can be extended to include attack logic.
        :param drone: The drone that is attacking.
        :param target: The target to attack.
        :param oai: Obstacle Avoidance Instance for pathfinding.
        :param grid: The grid used for pathfinding.
        """
        if not self.alive:
            return
        
        # Convert position array to tuple
        start_pos = (float(self.position[0]), float(self.position[1]))
        target_pos = (float(target.x()), float(target.y()))
        
        self.guiding_missile = GuidingMissile(drone, target, oai, grid)
        self.guiding_missile.shootMissile(start_pos, target_pos)
        
