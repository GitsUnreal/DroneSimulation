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
        self.oai.add_neighbors(self.grid)

        print(f"MainController initialized with {len(self.drones)} drones and {len(self.obstacles)} obstacles.")
        print(f"Grid created with {len(self.grid)} cells.")

    @staticmethod
    def snap_to_grid(pos):
        x = max(0, min(round(pos[0] / CELL_SIZE) * CELL_SIZE, WIDTH - CELL_SIZE))
        y = max(0, min(round(pos[1] / CELL_SIZE) * CELL_SIZE, HEIGHT - CELL_SIZE))
        return (x, y)

    def distance_to_target(self, drone):
        return np.linalg.norm(np.array([self.target.x(), self.target.y()]) - drone.position)

    def update_drones(self):
        for i, drone in enumerate(self.drones):
            if drone.is_destroyed():
                continue

            drone.update_position_sync()
            target_vec = np.array([self.target.x(), self.target.y()]) - drone.position
            distance = np.linalg.norm(target_vec)

            sep = self.boids.compute_separation(drone) * 2.0
            ali = self.boids.compute_alignment(drone) * 0.1
            coh = self.boids.compute_cohesion(drone) * 0.1
            target_force = (target_vec / distance) * 1.5 if distance > 5 else np.zeros(2)

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

            if not hasattr(drone, 'current_path') or not drone.current_path:
                if collision_detected:
                    start = self.snap_to_grid(drone.position)
                    goal = self.snap_to_grid((self.target.x(), self.target.y()))
                    path = self.oai.find_path(self.grid, start, goal, drone)
                    drone.current_path = path or []
                    drone.current_waypoint_index = 0
                    drone.path_id = f"drone_{i}_path_{len(drone.current_path)}"

            # Movement logic
            if collision_detected and not drone.current_path:
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

            drone.velocity += steering * (0.2 if collision_detected else 0.1)
            drone.velocity = self.boids.limit_speed(drone.velocity)
            drone.position += drone.velocity
            drone.constrain_to_bounds(WIDTH, HEIGHT)
            drone.sync_from_position()

            if self.distance_to_target(drone) < 100 and not drone.has_attacked:
                if drone.can_fire_missile():
                    print(f"Drone {drone.drone_id} attacking target.")
                    drone.attack(drone, self.target, self.oai, self.grid)
                    if drone.missiles_fired >= drone.max_missiles:
                        drone.has_attacked = True
                        print(f"Drone {drone.drone_id} has no missiles left and is returning.")
                else:
                    print(f"Drone {drone.drone_id} is out of missiles.")
                    drone.has_attacked = True

            if drone.has_attacked:
                drone.current_path = []
                start = self.snap_to_grid(drone.position)
                base_goal = self.snap_to_grid((self.base.x(), self.base.y()))
                path = self.oai.find_path(self.grid, start, base_goal, drone)
                drone.current_path = path or []
                drone.current_waypoint_index = 0
                drone.path_id = f"drone_{i}_base_path_{len(drone.current_path)}"
