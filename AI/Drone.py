import numpy as np
from .GuidingMissile import GuidingMissile

class Drone:
    def __init__(self, position, velocity):
        """
        Initialize a drone with position (x, y) and velocity (vx, vy).
        :param x: Initial x-coordinate of the drone.
        :param y: Initial y-coordinate of the drone.
        :param vx: Velocity in the x-direction.
        :param vy: Velocity in the y-direction.
        """

        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.x, self.y = self.position
        self.alive = True

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
    
    def attack(self, target):
        """
        Attack the target.
        This method can be extended to include attack logic.
        :param target: The target to attack.
        """
        if not self.alive:
            return
        GuidingMissile(target)  # Placeholder for missile logic
        