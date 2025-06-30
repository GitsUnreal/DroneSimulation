class Drone:
    def __init__(self, x, y, vx=2, vy=1):
        """
        Initialize a drone with position (x, y) and velocity (vx, vy).
        :param x: Initial x-coordinate of the drone.
        :param y: Initial y-coordinate of the drone.
        :param vx: Velocity in the x-direction.
        :param vy: Velocity in the y-direction.
        """

        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
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
            self.x += self.vx
        elif self.x > target.x() + target.width():
            self.x -= self.vx
        if self.y < target.y():
            self.y += self.vy
        elif self.y > target.y() + target.height():
            self.y -= self.vy
        
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
        # Logic for attacking the target can be added here
        pass

    def apply_boids_behavior(self, drones):
        """
        Apply Boids behavior to the drone based on nearby drones.
        This method can be extended to include flocking behavior.
        :param drones: List of all drones in the simulation.
        """
        # Placeholder for Boids behavior logic
        pass