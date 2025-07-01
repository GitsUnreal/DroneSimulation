from AI.ObstacleAvoidance import OAI
from AI.Boids import Boids
import numpy as np

WIDTH = 1080
HEIGHT = 720
CELL_SIZE = 20

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
        self.oai = OAI(self.drones, self.obstacles, CELL_SIZE)
        self.grid = self.oai.make_grid()
        self.oai.add_neighbors(self.grid)
        self.path = None
        print(f"MainController initialized with {len(self.drones)} drones, {len(self.obstacles)} obstacles")
        print(f"Grid created with {len(self.grid)} cells")

    @staticmethod
    def snap_to_grid(pos):
        x = int(round(pos[0] / CELL_SIZE) * CELL_SIZE)
        y = int(round(pos[1] / CELL_SIZE) * CELL_SIZE)
        x = max(0, min(x, WIDTH - CELL_SIZE))
        y = max(0, min(y, HEIGHT - CELL_SIZE))
        return (x, y)

    def move_drones(self):
        for i, drone in enumerate(self.drones):
            if drone.is_destroyed():
                continue

            # Sync position before calculation
            drone.update_position_sync()
            
            # Get target direction
            target_pos = np.array([self.target.x(), self.target.y()])
            to_target = target_pos - drone.position
            distance_to_target = np.linalg.norm(to_target)
            
            # Compute boids forces with stronger separation
            sep = self.boids.compute_separation(drone) * 2.0
            ali = self.boids.compute_alignment(drone) * 0.1
            coh = self.boids.compute_cohesion(drone) * 0.1
            
            # Target seeking force
            if distance_to_target > 5:
                target_force = (to_target / distance_to_target) * 1.5
            else:
                target_force = np.zeros(2)
            
            # IMPROVED COLLISION DETECTION - Check multiple steps ahead
            collision_detected = False
            obstacle_avoidance_force = np.zeros(2)
            
            # Check current position + immediate vicinity for obstacles
            for step in range(1, 10):  # Check 10 steps ahead instead of 5
                future_pos = drone.position + drone.velocity * step
                
                for obstacle in self.obstacles:
                    # Create a safety margin around obstacles
                    safety_margin = 25  # pixels
                    expanded_obstacle = {
                        'x': obstacle.x() - safety_margin,
                        'y': obstacle.y() - safety_margin,
                        'width': obstacle.width() + 2 * safety_margin,
                        'height': obstacle.height() + 2 * safety_margin
                    }
                    
                    # Check if future position would be in expanded obstacle area
                    if (expanded_obstacle['x'] <= future_pos[0] <= expanded_obstacle['x'] + expanded_obstacle['width'] and
                        expanded_obstacle['y'] <= future_pos[1] <= expanded_obstacle['y'] + expanded_obstacle['height']):
                        collision_detected = True
                        
                        # Calculate immediate avoidance force
                        obs_center = np.array([obstacle.x() + obstacle.width()/2, 
                                             obstacle.y() + obstacle.height()/2])
                        to_obstacle = obs_center - drone.position
                        distance_to_obs = np.linalg.norm(to_obstacle)
                        
                        if distance_to_obs > 0:
                            # Strong repulsion force inversely proportional to distance
                            avoidance = -(to_obstacle / distance_to_obs) * (100 / (distance_to_obs + 1))
                            obstacle_avoidance_force += avoidance
                        
                        break
                
                if collision_detected:
                    break
            
            # Individual pathfinding for each drone
            if not hasattr(drone, 'current_path') or not drone.current_path:
                if collision_detected:
                    # Find individual path for this specific drone
                    start = self.snap_to_grid(drone.position)
                    goal = self.snap_to_grid((self.target.x(), self.target.y()))
                    
                    # Each drone gets its own path calculation
                    path = self.oai.find_path(self.grid, start, goal, drone)
                    drone.current_path = path if path else []
                    drone.current_waypoint_index = 0
                    drone.path_id = f"drone_{i}_path_{len(drone.current_path)}"
                    print(f"Drone {drone.id}: Individual path calculated with {len(drone.current_path)} waypoints (ID: {drone.path_id})")
        
            # Determine movement strategy
            if collision_detected and (not hasattr(drone, 'current_path') or not drone.current_path):
                # EMERGENCY AVOIDANCE - No path found, use immediate obstacle avoidance
                print(f"Drone {drone.id}: Emergency avoidance activated!")
                steering = sep * 4.0 + obstacle_avoidance_force * 3.0  # Strong avoidance
                
                # Also try to move perpendicular to obstacle
                if np.linalg.norm(obstacle_avoidance_force) > 0:
                    perpendicular = np.array([-obstacle_avoidance_force[1], obstacle_avoidance_force[0]])
                    perpendicular = perpendicular / (np.linalg.norm(perpendicular) + 1e-6)
                    steering += perpendicular * 1.0
                
            elif hasattr(drone, 'current_path') and drone.current_path and drone.current_waypoint_index < len(drone.current_path):
                # Follow individual waypoints
                current_waypoint = np.array(drone.current_path[drone.current_waypoint_index])
                to_waypoint = current_waypoint - drone.position
                distance_to_waypoint = np.linalg.norm(to_waypoint)
                
                # Check if we've reached the current waypoint
                if distance_to_waypoint < 25:  # Increased threshold for more reliable waypoint following
                    drone.current_waypoint_index += 1
                    print(f"Drone {drone.id}: Reached waypoint {drone.current_waypoint_index-1}")
                    
                    # Check if we've reached the end of the path
                    if drone.current_waypoint_index >= len(drone.current_path):
                        drone.current_path = []
                        drone.current_waypoint_index = 0
                        print(f"Drone {drone.id}: Path completed")
                
                # Move towards current waypoint if we still have one
                if drone.current_waypoint_index < len(drone.current_path):
                    waypoint_force = (to_waypoint / (distance_to_waypoint + 1e-6)) * 2.0
                    # Add obstacle avoidance even while following path
                    steering = sep * 3.0 + waypoint_force * 2.0 + obstacle_avoidance_force * 1.5
                else:
                    # No more waypoints, use direct movement
                    steering = sep * 2.0 + ali + coh + target_force + obstacle_avoidance_force
            else:
                # Direct movement towards target with collision avoidance
                steering = sep * 2.0 + ali + coh + target_force + obstacle_avoidance_force

            # Apply steering with smoothing but allow faster response to obstacles
            if collision_detected:
                drone.velocity += steering * 0.2  # Faster response when collision detected
            else:
                drone.velocity += steering * 0.1  # Normal smooth movement
                
            drone.velocity = self.boids.limit_speed(drone.velocity)

            # Update position and constrain to bounds
            drone.position += drone.velocity
            drone.constrain_to_bounds(WIDTH, HEIGHT)
            drone.sync_from_position()

