from AI.ObstacleAvoidance import OAI

class MovementController:
    """
    MovementController class to manage the movement of drones and obstacles.
    This class handles the logic for moving drones towards their targets,
    avoiding obstacles, and updating their positions.
    """

    def __init__(self, drones, obstacles, target):
        self.drones = drones
        self.obstacles = obstacles
        self.target = target

        self.oai = OAI(self.drones, self.obstacles)
        self.grid = self.oai.make_grid()
        self.oai.add_neighbors(self.grid)
        self.path = None


    def move_drones(self):
        """
        Move drones towards the target while avoiding obstacles.
        This method iterates through each drone and updates its position
        based on the target's position and the obstacles in the environment.
        """
        for drone in self.drones:
            if not drone.is_destroyed():
                # Snap to grid positions
                start_x = (int(drone.x) // 20) * 20
                start_y = (int(drone.y) // 20) * 20
                goal_x = (int(self.target.x()) // 20) * 20
                goal_y = (int(self.target.y()) // 20) * 20
                
                start_pos = (start_x, start_y)
                goal_pos = (goal_x, goal_y)
                
                # Only find path if start position is in grid
                if start_pos in self.grid and goal_pos in self.grid:
                    self.path = self.oai.find_path(self.grid, start_pos, goal_pos)
                    if self.path and len(self.path) > 0:
                        next_step = self.path[0]
                        drone.move_to(next_step[0], next_step[1])
                        continue
                
                # Fallback to direct movement
                drone.move_towards_target(800, 600, self.target)
                
    def Boids(self):
        """
        Placeholder for Boids algorithm implementation.
        This method can be used to implement flocking behavior among drones.
        """
        # Implement Boids algorithm logic here
        pass