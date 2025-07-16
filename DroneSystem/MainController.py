import numpy as np

from DroneSystem.Movement.Navigation.ObstacleAvoidance import OAI
from DroneSystem.Movement.Behaviors.Boids import Boids
from DroneSystem.Combat.Weapons.MissileManager import MissileManager, MissileType
from GUI.Widgets.SpeedControlWidget import SpeedControlWidget

WIDTH, HEIGHT, CELL_SIZE = 1080, 720, 20

class MainController:
    def __init__(self, drones, obstacles=None, target=None, base=None, sim_modes=None, alert_system=None):
        self.drones = drones
        self.obstacles = obstacles or []
        self.target = target
        self.base = base
        self.sim_modes = sim_modes
        self.alert_system = alert_system

        self.boids = Boids(self.drones)
        self.oai = OAI(self.drones, self.obstacles, CELL_SIZE)
        self.grid = self.oai.make_grid()
        self.oai.add_neighbors(self.grid)
        
        # REMOVE: self.radar = Radar(self.drones, self.obstacles, self.target)

        # Add missile manager with grid reference
        self.missile_manager = MissileManager(self.oai, self.grid)
        
        # Set target in missile manager
        if self.target:
            self.missile_manager.set_target(self.target)

        # Apply initial mode settings if provided
        if self.sim_modes:
            self.sim_modes.apply_mode_to_simulation(drones, target)

        #print(f"MainController initialized with {len(self.drones)} drones and {len(self.obstacles)} obstacles.")
        #print(f"Grid created with {len(self.grid)} cells.")

        self.simulation_speed = 1.0
        self.speed_control = SpeedControlWidget()
        self.speed_control.speed_changed.connect(self.set_simulation_speed)
        
        self.mission_complete_alerted = False  # Add this flag
    
    def set_simulation_speed(self, speed):
        self.simulation_speed = speed
        # Update timer interval based on speed
        if hasattr(self, 'timer'):
            new_interval = max(1, int(self.base_interval / speed))
            self.timer.setInterval(new_interval)
            
    def distance_to_target(self, drone):
        """Calculate distance from drone to target."""
        return np.linalg.norm(np.array([self.target.position[0], self.target.position[1]]) - drone.position)
    
    def distance_to_base(self, drone):
        """Calculate distance from drone to base."""
        return np.linalg.norm(np.array([self.base.x(), self.base.y()]) - drone.position)

    def get_path_to_target(self, drone, goal_pos):
        """Get pathfinding route to a specific goal position."""
        start = self.oai.snap_to_grid(drone.position)
        goal = self.oai.snap_to_grid(goal_pos)
        return self.oai.find_path(self.grid, start, goal, drone)

    def update_drones(self, simulation_step=0):
        # Get movement parameters from current mode
        movement_params = self.sim_modes.get_current_handler().get_movement_parameters() if self.sim_modes else {
            'separation_weight': 2.0,
            'alignment_weight': 0.1, 
            'cohesion_weight': 0.1,
            'target_weight': 1.5
        }
        
        # REMOVE: visible_obstacles = self.radar.update_radar()
        
        # Update target movement FIRST
        if self.target and self.target.is_moving_target:
            self.target.update_movement()
            
            # Update missile manager with new target position
            self.missile_manager.set_target(self.target)
        
        # Update missiles FIRST (before drone logic)
        self.missile_manager.update_missiles(0.05, self.drones, self.obstacles)
        
        # Check for target hits and destruction
        target_hit_this_frame = False
        for missile in self.missile_manager.get_active_missiles():
            if hasattr(missile, 'hit_target') and missile.hit_target and missile.state.value == "exploding":
                if not self.target.is_destroyed():
                    #print(f"🎯 TARGET HIT by missile {missile.missile_id}!")
                    self.target.destroy()
                    target_hit_this_frame = True
        
        # Return target hit status so GUI can handle it
        if target_hit_this_frame:
            return {'target_destroyed': True}
        
        for i, drone in enumerate(self.drones):
            # Skip destroyed drones AND landed drones
            if drone.is_destroyed() or (hasattr(drone, 'has_landed') and drone.has_landed):
                continue

            drone.update_position_sync()
            
            # Initialize steering to zero vector
            steering = np.zeros(2)

            # Determine target based on drone state
            if hasattr(drone, 'returning_to_base') and drone.returning_to_base:
                # When returning to base, target the base instead of the mission target
                target_vec = np.array([self.base.x(), self.base.y()]) - drone.position
                target_force = (target_vec / (np.linalg.norm(target_vec) + 1e-6)) * 2.0  # Stronger force to base
            elif drone.state == "search" and hasattr(drone, "search_waypoint"):
                target_vec = drone.search_waypoint - drone.position
                distance = np.linalg.norm(target_vec)
                target_force = (target_vec / (distance + 1e-6)) * 1.5 if distance > 5 else np.zeros(2)
            else:
                # Normal mission: target the mission objective
                target_vec = np.array([self.target.position[0], self.target.position[1]]) - drone.position
                distance = np.linalg.norm(target_vec)
                target_force = (target_vec / distance) * 1.5 if distance > 5 else np.zeros(2)

            # Boids forces
            sep = self.boids.compute_separation(drone) * movement_params['separation_weight']
            ali = self.boids.compute_alignment(drone) * movement_params['alignment_weight']
            coh = self.boids.compute_cohesion(drone) * movement_params['cohesion_weight']

            # Obstacle avoidance
            avoidance_force = np.zeros(2)
            collision_detected = False

            for step in range(1, 10):
                future_pos = drone.position + drone.velocity * step
                for obs in self.obstacles:
                    margin = 60
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
                    path = self.get_path_to_target(drone, (self.target.position[0], self.target.position[1]))
                    drone.current_path = path or []
                    drone.current_waypoint_index = 0
                    drone.path_id = f"drone_{i}_path_{len(drone.current_path)}"

            # Movement logic - updated to prioritize base return
            if hasattr(drone, 'returning_to_base') and drone.returning_to_base:
                base_distance = self.distance_to_base(drone)
                
                # If very close to base, move directly without pathfinding
                if base_distance < 50:
                    # Direct movement to base when close
                    base_vec = np.array([self.base.x(), self.base.y()]) - drone.position
                    base_distance_vec = np.linalg.norm(base_vec)
                    if base_distance_vec > 0:
                        direct_force = (base_vec / base_distance_vec) * 4.0  # Strong direct force
                        steering = sep * 0.5 + direct_force + avoidance_force * 0.5  # Reduced separation when landing
                    else:
                        steering = np.zeros(2)
                else:
                    # Use pathfinding when far from base
                    if drone.current_path and drone.current_waypoint_index < len(drone.current_path):
                        waypoint = np.array(drone.current_path[drone.current_waypoint_index])
                        to_waypoint = waypoint - drone.position
                        dist = np.linalg.norm(to_waypoint)
                        if dist < 25:
                            drone.current_waypoint_index += 1
                            if drone.current_waypoint_index >= len(drone.current_path):
                                drone.current_path = []
                                drone.current_waypoint_index = 0
                                #print(f"Drone {drone.drone_id} completed return path.")
                        
                        if drone.current_waypoint_index < len(drone.current_path):
                            force = (to_waypoint / (dist + 1e-6)) * 3.0
                            steering = sep * 1.0 + force * 3 + avoidance_force * 1.0
                        else:
                            # No path, go directly to base
                            steering = sep * 1.0 + target_force * 3 + avoidance_force
                    else:
                        # No path, go directly to base
                        steering = sep * 1.0 + target_force * 3 + avoidance_force
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
                # Advance waypoint if close enough (increase threshold to 25)
                if dist < 25:
                    drone.current_waypoint_index += 1
                    if drone.current_waypoint_index >= len(drone.current_path):
                        drone.current_path = []
                        drone.current_waypoint_index = 0
                # Move toward waypoint if path remains
                if drone.current_waypoint_index < len(drone.current_path):
                    speed = drone.get_current_speed() if hasattr(drone, 'get_current_speed') else 5.0
                    move_vec = (to_waypoint / (dist + 1e-6)) * speed
                    drone.velocity = move_vec
                    drone.position += drone.velocity
                    drone.sync_from_position()
            else:
                steering = sep * 2 + ali + coh + target_force + avoidance_force

            # Apply movement
            desired_speed = getattr(drone.movement_config, "speed", 2.0)

            # Combine velocity and steering
            final_velocity = drone.velocity + steering

            # Always normalize and scale to desired speed
            norm = np.linalg.norm(final_velocity)
            if norm > 0:
                final_velocity = (final_velocity / norm) * desired_speed
            else:
                final_velocity = np.zeros(2)

            drone.velocity = final_velocity
            drone.position += drone.velocity
            drone.constrain_to_bounds(WIDTH, HEIGHT)
            drone.sync_from_position()

            # Modified attack logic to use new missile system
            if self.distance_to_target(drone) < 100 and not drone.has_attacked:
                if drone.can_fire_missile():
                    # Use predicted position for moving targets
                    if self.target.is_moving_target:
                        target_pos = self.target.get_predicted_position(1.0)  # Predict 1 second ahead
                        #print(f"Drone {drone.drone_id} targeting predicted position {target_pos}")
                    else:
                        target_pos = (self.target.x(), self.target.y())
                    
                    success = self.missile_manager.fire_missile(
                        drone, 
                        target_pos, 
                        MissileType.HOMING  # Use homing missiles for moving targets
                    )
                    
                    if success and drone.missiles_fired >= drone.max_missiles:
                        drone.has_attacked = True
                        #print(f"Drone {drone.drone_id} has no missiles left and is returning.")
                else:
                    drone.has_attacked = True

            # Return to base logic - FIXED
            if drone.has_attacked:
                if not hasattr(drone, 'returning_to_base'):
                    drone.returning_to_base = True
                    path = self.get_path_to_target(drone, (self.base.x(), self.base.y()))
                    drone.current_path = path or []
                    drone.current_waypoint_index = 0
                    drone.path_id = f"drone_{i}_base_path_{len(drone.current_path)}"
                    #print(f"Drone {drone.drone_id} returning to base with {len(drone.current_path)} waypoints.")
                
                # Check if drone has reached base - INCREASED RADIUS
                base_distance = self.distance_to_base(drone)
                if base_distance < 30:  # Increased from 10 to 30 pixels
                    # Position drone exactly at base with offset to avoid overlap
                    landed_drones_count = len([d for d in self.drones if hasattr(d, 'has_landed') and d.has_landed])
                    offset_x = (landed_drones_count % 3) * 15  # Spread drones in a 3x3 grid
                    offset_y = (landed_drones_count // 3) * 15
                    
                    drone.position = np.array([
                        self.base.x() + 5 + offset_x, 
                        self.base.y() + 5 + offset_y
                    ], dtype=float)
                    drone.sync_from_position()
                    
                    # Stop drone movement completely
                    drone.velocity = np.zeros(2)
                    
                    # Clear path to stop circling
                    drone.current_path = []
                    drone.current_waypoint_index = 0
                    
                    drone.land_at_base()
                    drone.returning_to_base = False
                    
                    # Clear active missiles
                    if hasattr(drone, 'missiles'):
                        drone.missiles.clear()
                    
                    #print(f"Drone {drone.drone_id} has landed at base (distance: {base_distance:.1f}) and is now hidden.")
        
        for drone in self.drones:
            if getattr(drone, "has_attacked", False) or getattr(drone, "missiles_left", 1) == 0:
                drone.state = "return"
                self._move_drone_to_base(drone)
            elif hasattr(self.target, 'hidden') and self.target.hidden and not getattr(self.target, 'spotted_by_radar', False):
                drone.state = "search"
                self._move_drone_in_search_pattern(drone, simulation_step)
                # self._move_drone_in_reconnaissance_pattern(drone, simulation_step)
            else:
                drone.state = "attack"
                self._move_drone_towards_target(drone, self.target)
        
        # ALERTS
        for drone in self.drones:
            if not drone.alive and not hasattr(drone, '_destruction_alerted'):
                self.alert_system.show_drone_destroyed_alert(drone.drone_id)
                drone._destruction_alerted = True

            if drone.missiles_fired >= drone.max_missiles and not hasattr(drone, '_missiles_alerted'):
                self.alert_system.show_all_missiles_fired_alert(drone.drone_id)
                drone._missiles_alerted = True

            if hasattr(drone, 'has_landed') and drone.has_landed and not hasattr(drone, '_landing_alerted'):
                self.alert_system.show_drone_landed_alert(drone.drone_id)
                drone._landing_alerted = True

        # Mission complete alert (only once)
        if (all(hasattr(drone, 'has_landed') and drone.has_landed for drone in self.drones) 
            and not self.mission_complete_alerted):
            self.alert_system.show_mission_complete_alert(self.drones)
            self.mission_complete_alerted = True
        
        return {'target_destroyed': False}

    def _move_drone_in_search_pattern(self, drone, simulation_step):
        # Initialize search phase if not set
        if not hasattr(drone, "search_phase"):
            drone.search_phase = 0

        # Screen center
        center_screen = np.array([WIDTH / 2, HEIGHT / 2])

        if drone.search_phase == 0:
            # First phase: fly from base to center of screen
            drone.search_waypoint = center_screen
            # Check if drone is close to center
            if np.linalg.norm(drone.position - center_screen) < 30:
                drone.search_phase = 1  # Switch to spiral search
        else:
            # Spiral search pattern (as waypoint)
            angle = (drone.drone_id * 45 + simulation_step * 4) % 360
            radius = 50 + simulation_step * 2 + (drone.drone_id * 10)
            center = center_screen
            search_waypoint = center + np.array([
                radius * np.cos(np.deg2rad(angle)),
                radius * np.sin(np.deg2rad(angle))
            ])
            drone.search_waypoint = search_waypoint  # Store as attribute

    def _move_drone_in_reconnaissance_pattern(self, drone, simulation_step):
        board_width = 800
        board_height = 600
        rows = len(self.drones)
        row = drone.drone_id % rows
        sweep_speed = 2
        x = (simulation_step * sweep_speed) % board_width
        y = board_height * (row + 1) / (rows + 1)
        drone.search_waypoint = np.array([x, y])

    def _move_drone_towards_target(self, drone, target):
        # Move directly toward target center
        target_center = np.array([target.position[0] + target.width / 2, target.position[1] + target.height / 2])
        direction = target_center - drone.position
        if np.linalg.norm(direction) > 1:
            direction = direction / np.linalg.norm(direction)
            speed = getattr(drone.movement_config, "speed", 5.0)  # fallback to 5.0 if missing
            drone.position += direction * speed
        drone.sync_from_position()
    
    def _move_drone_to_base(self, drone):
        base_pos = np.array([self.base.x(), self.base.y()])
        direction = base_pos - drone.position
        if np.linalg.norm(direction) > 1:
            direction = direction / np.linalg.norm(direction)
            speed = getattr(drone.movement_config, "speed", 5.0)
            drone.position += direction * speed
        drone.sync_from_position()

    def handle_drone_destroyed(self, drone):
        self.alert_system.show_alert(f"Drone {drone.drone_id} destroyed!", color="red")
