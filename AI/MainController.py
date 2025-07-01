from AI.ObstacleAvoidance import OAI
from AI.Boids import Boids
import numpy as np

WIDTH, HEIGHT, CELL_SIZE = 1080, 720, 20

class MainController:
    def __init__(self, drones, obstacles=None, target=None, base=None):
        self.drones = drones
        self.obstacles = obstacles or []
        self.target = target
        self.base = base

        self.boids = Boids(self.drones)
        self.oai = OAI(self.drones, self.obstacles, CELL_SIZE)
        self.grid = self.oai.make_grid()
        self.oai.add_neighbors(self.grid)  # Only call once here

        print(f"MainController initialized with {len(self.drones)} drones and {len(self.obstacles)} obstacles.")
        print(f"Grid created with {len(self.grid)} cells.")

    def distance_to_target(self, drone):
        """Calculate distance from drone to target."""
        return np.linalg.norm(np.array([self.target.x(), self.target.y()]) - drone.position)
    
    def distance_to_base(self, drone):
        """Calculate distance from drone to base."""
        return np.linalg.norm(np.array([self.base.x(), self.base.y()]) - drone.position)

    def get_path_to_target(self, drone, goal_pos):
        """Get pathfinding route to a specific goal position."""
        start = self.oai.snap_to_grid(drone.position)
        goal = self.oai.snap_to_grid(goal_pos)
        return self.oai.find_path(self.grid, start, goal, drone)

    def update_drones(self):
        for i, drone in enumerate(self.drones):
            # Skip destroyed drones AND landed drones
            if drone.is_destroyed() or (hasattr(drone, 'has_landed') and drone.has_landed):
                continue

            drone.update_position_sync()
            
            # Determine target based on drone state
            if hasattr(drone, 'returning_to_base') and drone.returning_to_base:
                # When returning to base, target the base instead of the mission target
                target_vec = np.array([self.base.x(), self.base.y()]) - drone.position
                target_force = (target_vec / (np.linalg.norm(target_vec) + 1e-6)) * 2.0  # Stronger force to base
            else:
                # Normal mission: target the mission objective
                target_vec = np.array([self.target.x(), self.target.y()]) - drone.position
                distance = np.linalg.norm(target_vec)
                target_force = (target_vec / distance) * 1.5 if distance > 5 else np.zeros(2)

            # Boids forces
            sep = self.boids.compute_separation(drone) * 2.0
            ali = self.boids.compute_alignment(drone) * 0.1
            coh = self.boids.compute_cohesion(drone) * 0.1

            # Obstacle avoidance
            avoidance_force = np.zeros(2)
            collision_detected = False

            for step in range(1, 10):
                future_pos = drone.position + drone.velocity * step
                for obs in self.obstacles:
                    margin = 25
                    if (obs.x() - margin <= future_pos[0] <= obs.x() + obs.width() + margin and
                        obs.y() - margin <= future_pos[1] <= obs.y() + obs.height() + margin):
                        
                        obs_center = np.array([obs.x() + obs.width()/2, obs.y() + obs.height()/2])
                        to_obs = obs_center - drone.position
                        dist = np.linalg.norm(to_obs)
                        if dist > 0:
                            avoidance_force += -(to_obs / dist) * (100 / (dist + 1))
                        collision_detected = True
                        break
                if collision_detected:
                    break

            # Drone-to-drone collision avoidance - only with active drones
            for other in self.drones:
                if (other is not drone and 
                    other.alive and 
                    not (hasattr(other, 'has_landed') and other.has_landed)):
                    dist = np.linalg.norm(drone.position - other.position)
                    if dist < 20:
                        direction = drone.position - other.position
                        if np.linalg.norm(direction) > 0:
                            direction /= np.linalg.norm(direction)
                            drone.position += direction * 2
                            other.position -= direction * 2

            # Pathfinding for obstacles
            if not hasattr(drone, 'current_path') or not drone.current_path:
                if collision_detected:
                    path = self.get_path_to_target(drone, (self.target.x(), self.target.y()))
                    drone.current_path = path or []
                    drone.current_waypoint_index = 0
                    drone.path_id = f"drone_{i}_path_{len(drone.current_path)}"

            # Movement logic - updated to prioritize base return
            if hasattr(drone, 'returning_to_base') and drone.returning_to_base:
                # When returning to base, prioritize direct movement to base
                if drone.current_path and drone.current_waypoint_index < len(drone.current_path):
                    waypoint = np.array(drone.current_path[drone.current_waypoint_index])
                    to_waypoint = waypoint - drone.position
                    dist = np.linalg.norm(to_waypoint)
                    if dist < 25:
                        drone.current_waypoint_index += 1
                        if drone.current_waypoint_index >= len(drone.current_path):
                            drone.current_path = []
                            drone.current_waypoint_index = 0
                            print(f"Drone {drone.drone_id} completed return path.")
                
                if drone.current_waypoint_index < len(drone.current_path):
                    force = (to_waypoint / (dist + 1e-6)) * 3.0  # Stronger force for return
                    steering = sep * 1.5 + force * 3 + avoidance_force * 1.5  # Reduce separation, increase path following
                else:
                    # No path, go directly to base
                    steering = sep * 1.5 + target_force * 3 + avoidance_force
            elif collision_detected and not drone.current_path:
                steering = sep * 4 + avoidance_force * 3
                if np.linalg.norm(avoidance_force) > 0:
                    perpendicular = np.array([-avoidance_force[1], avoidance_force[0]])
                    perpendicular /= np.linalg.norm(perpendicular) + 1e-6
                    steering += perpendicular
            elif drone.current_path and drone.current_waypoint_index < len(drone.current_path):
                waypoint = np.array(drone.current_path[drone.current_waypoint_index])
                to_waypoint = waypoint - drone.position
                dist = np.linalg.norm(to_waypoint)
                if dist < 25:
                    drone.current_waypoint_index += 1
                    if drone.current_waypoint_index >= len(drone.current_path):
                        drone.current_path = []
                        drone.current_waypoint_index = 0
                        print(f"Drone {drone.drone_id} completed path.")
                if drone.current_waypoint_index < len(drone.current_path):
                    force = (to_waypoint / (dist + 1e-6)) * 2.0
                    steering = sep * 3 + force * 2 + avoidance_force * 1.5
                else:
                    steering = sep * 2 + ali + coh + target_force + avoidance_force
            else:
                steering = sep * 2 + ali + coh + target_force + avoidance_force

            # Apply movement
            drone.velocity += steering * (0.2 if collision_detected else 0.1)
            drone.velocity = self.boids.limit_speed(drone.velocity)
            drone.position += drone.velocity
            drone.constrain_to_bounds(WIDTH, HEIGHT)
            drone.sync_from_position()

            # Attack logic - FIXED to allow multiple missiles
            if self.distance_to_target(drone) < 100 and not drone.has_attacked:
                if drone.can_fire_missile():
                    print(f"Drone {drone.drone_id} attacking target.")
                    drone.attack(drone, self.target, self.oai, self.grid)
                    
                    # Only mark as attacked when all missiles are used
                    if drone.missiles_fired >= drone.max_missiles:
                        drone.has_attacked = True
                        print(f"Drone {drone.drone_id} has no missiles left and is returning.")
                else:
                    print(f"Drone {drone.drone_id} is out of missiles.")
                    drone.has_attacked = True

            # Return to base logic - FIXED
            if drone.has_attacked:
                if not hasattr(drone, 'returning_to_base'):
                    drone.returning_to_base = True
                    path = self.get_path_to_target(drone, (self.base.x(), self.base.y()))
                    drone.current_path = path or []
                    drone.current_waypoint_index = 0
                    drone.path_id = f"drone_{i}_base_path_{len(drone.current_path)}"
                    print(f"Drone {drone.drone_id} returning to base with {len(drone.current_path)} waypoints.")
                
                # Check if drone has reached base
                if self.distance_to_base(drone) < 10:
                    # Position drone exactly at base
                    drone.position = np.array([self.base.x() + 10, self.base.y() + 10], dtype=float)
                    drone.sync_from_position()
                    
                    # Stop drone movement
                    drone.velocity = np.zeros(2)
                    
                    drone.land_at_base()
                    drone.returning_to_base = False
                    
                    # Clear active missiles
                    if hasattr(drone, 'missiles'):
                        drone.missiles.clear()
                    
                    print(f"Drone {drone.drone_id} has landed at base and is now hidden.")
