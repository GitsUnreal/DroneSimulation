from AI.ObstacleAvoidance import OAI
from AI.Boids import Boids
import numpy as np

class MainController:
    """
    MovementController class to manage the movement of drones and obstacles.
    This class handles the logic for moving drones towards their targets,
    avoiding obstacles, and updating their positions.
    """

    def __init__(self, drones, obstacles, target):
        """
        Initialize the MovementController with drones, obstacles, and target.
        :param drones: List of drone objects that will be controlled.
        :param obstacles: List of obstacle objects that drones need to avoid.
        :param target: The target position that drones will move towards.
        """
        self.drones = drones
        self.obstacles = obstacles
        self.target = target

        # Initialize Boids and OAI with drones and their velocities
        self.boids = Boids(self.drones)
        self.oai = OAI(self.drones, self.obstacles)
        self.grid = self.oai.make_grid()
        self.oai.add_neighbors(self.grid)
        self.path = None


    def move_drones(self):
        for drone in self.drones:
            if drone.is_destroyed():
                continue

            start = (int(drone.x) // 20) * 20
            goal = (int(self.target.center().x()), int(self.target.center().y()))

            path = self.oai.find_path(self.grid, (start, start), goal)

            if path:
                next_pos = np.array(path[0])
                avoidance_vector = next_pos - np.array(start)

                avoidance = avoidance_vector / (np.linalg.norm(avoidance_vector) + 1e-6)  # Avoid division by zero
            else:
                avoidance = np.zeros(2)  # No path found, no avoidance
            

        # Combine with Boids behavior and target attraction
        sep = self.boids.compute_separation(drone)
        ali = self.boids.compute_alignment(drone)
        coh = self.boids.compute_cohesion(drone)
        steering = 1.5 * sep + 1.0 * ali + 1.0 * coh + 2.0 * avoidance

        to_target = goal - np.array(start)
        if np.linalg.norm(to_target) > 1:
            to_target = to_target / np.linalg.norm(to_target)
        steering += 0.2 * to_target

        drone.velocity += steering
        drone.velocity = self.boids.limit_speed(drone.velocity)
        drone.position += drone.velocity
        drone.x, drone.y = drone.position
                
