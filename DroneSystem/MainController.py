import numpy as np
from SimMode.Modes import Modes  # Add this import at the top

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
        target_pos = self.get_target_position()
        return np.linalg.norm(target_pos - drone.position)
    
    def distance_to_base(self, drone):
        """Calculate distance from drone to base."""
        if self.base is None:
            return float('inf')
        
        # Handle QRect base object
        if hasattr(self.base, 'x') and hasattr(self.base, 'y'):
            base_pos = np.array([self.base.x(), self.base.y()])
        else:
            # Fallback for other base types
            base_pos = np.array([self.base.position[0], self.base.position[1]])
        
        return np.linalg.norm(drone.position - base_pos)

    def get_base_position(self):
        """Get base position as numpy array"""
        if self.base is None:
            return np.array([50.0, 50.0])  # Default fallback
        
        # Handle QRect base object
        if hasattr(self.base, 'x') and hasattr(self.base, 'y'):
            return np.array([float(self.base.x()), float(self.base.y())])
        else:
            # Fallback for other base types
            return np.array([self.base.position[0], self.base.position[1]])

    def get_target_position(self):
        """Get target position as a numpy array, handling different target types"""
        try:
            if not self.target:
                return np.array([740.0, 560.0])  # Default fallback
                
            # First try x() and y() methods (most common for GUI objects)
            if hasattr(self.target, 'x') and hasattr(self.target, 'y'):
                return np.array([float(self.target.x()), float(self.target.y())])
                
            # Then try position attribute
            if hasattr(self.target, 'position'):
                pos = self.target.position
                
                # Check if position is a list/tuple/array with at least 2 elements
                if hasattr(pos, '__len__'):
                    try:
                        if len(pos) >= 2:
                            return np.array([float(pos[0]), float(pos[1])])
                    except TypeError:
                        # len() failed, position might be a scalar
                        pass
                
                # If position is a scalar, use fallback
                if np.isscalar(pos):
                    return np.array([740.0, 560.0])
                    
                # Try to convert directly to float array
                try:
                    pos_array = np.array(pos, dtype=float)
                    if pos_array.size >= 2:
                        return pos_array.flatten()[:2]  # Take first 2 elements
                except:
                    pass
            
            # Final fallback
            return np.array([740.0, 560.0])
            
        except Exception as e:
            # Remove debug print: print(f"Error getting target position: {e}")
            return np.array([740.0, 560.0])
    
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
        
        # --- Modularized drone update loop ---
        from DroneSystem.Movement.Navigation.PathfindingManager import PathfindingManager
        from DroneSystem.Movement.CollisionManager import CollisionManager
        from DroneSystem.States.StateManager import StateManager
        from Utils.MathUtils import normalize, distance
        from DroneSystem.Controllers.AttackManager import AttackManager

        # Handle drone-to-drone collisions
        CollisionManager.handle_drone_collisions(self.drones)

        for i, drone in enumerate(self.drones):
            # Skip destroyed drones AND landed drones
            if drone.is_destroyed() or (hasattr(drone, 'has_landed') and drone.has_landed):
                continue

            drone.update_position_sync()
            steering = np.zeros(2)

            # State management (return to base, etc.)
            StateManager.update_drone_state(drone, self)

            # Target selection
            if hasattr(drone, 'returning_to_base') and drone.returning_to_base:
                base_pos = self.get_base_position()
                target_vec = base_pos - drone.position
                target_force = normalize(target_vec) * 2.0
            elif drone.state == "search" and hasattr(drone, "search_waypoint"):
                target_vec = drone.search_waypoint - drone.position
                dist = np.linalg.norm(target_vec)
                target_force = normalize(target_vec) * 1.5 if dist > 5 else np.zeros(2)
            else:
                try:
                    target_pos = self.get_target_position()
                    target_vec = target_pos - drone.position
                    dist = np.linalg.norm(target_vec)
                    target_force = normalize(target_vec) * 1.5 if dist > 5 else np.zeros(2)
                except Exception as e:
                    print(f"Error accessing target position: {e}")
                    target_force = np.zeros(2)

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
                            avoidance_force += -normalize(to_obs) * (100 / (dist + 1))
                        collision_detected = True
                        break
                if collision_detected:
                    break

            # Pathfinding for obstacles
            if not hasattr(drone, 'current_path') or not drone.current_path:
                if collision_detected:
                    target_pos = self.get_target_position()
                    path = PathfindingManager.find_path(self.oai, self.grid, drone.position, (target_pos[0], target_pos[1]), drone)
                    drone.current_path = path or []
                    drone.current_waypoint_index = 0
                    drone.path_id = f"drone_{i}_path_{len(drone.current_path)}"

            # Movement logic
            if hasattr(drone, 'returning_to_base') and drone.returning_to_base:
                base_distance = self.distance_to_base(drone)
                if base_distance < 50:
                    base_vec = np.array([self.base.x(), self.base.y()]) - drone.position
                    base_distance_vec = np.linalg.norm(base_vec)
                    if base_distance_vec > 0:
                        direct_force = normalize(base_vec) * 4.0
                        steering = sep * 0.5 + direct_force + avoidance_force * 0.5
                    else:
                        steering = np.zeros(2)
                else:
                    if drone.current_path and drone.current_waypoint_index < len(drone.current_path):
                        waypoint = np.array(drone.current_path[drone.current_waypoint_index])
                        to_waypoint = waypoint - drone.position
                        dist = np.linalg.norm(to_waypoint)
                        if dist < 25:
                            drone.current_waypoint_index += 1
                            if drone.current_waypoint_index >= len(drone.current_path):
                                drone.current_path = []
                                drone.current_waypoint_index = 0
                        if drone.current_waypoint_index < len(drone.current_path):
                            force = normalize(to_waypoint) * 3.0
                            steering = sep * 1.0 + force * 3 + avoidance_force * 1.0
                        else:
                            steering = sep * 1.0 + target_force * 3 + avoidance_force
                    else:
                        steering = sep * 1.0 + target_force * 3 + avoidance_force
            elif collision_detected and not drone.current_path:
                steering = sep * 4 + avoidance_force * 3
                if np.linalg.norm(avoidance_force) > 0:
                    perpendicular = np.array([-avoidance_force[1], avoidance_force[0]])
                    perpendicular = normalize(perpendicular)
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
                if drone.current_waypoint_index < len(drone.current_path):
                    speed = drone.get_current_speed() if hasattr(drone, 'get_current_speed') else 5.0
                    move_vec = normalize(to_waypoint) * speed
                    drone.velocity = move_vec
                    drone.position += drone.velocity
                    drone.sync_from_position()
            else:
                steering = sep * 2 + ali + coh + target_force + avoidance_force

            # Apply movement
            desired_speed = getattr(drone.movement_config, "speed", 2.0)
            final_velocity = drone.velocity + steering
            norm = np.linalg.norm(final_velocity)
            if norm > 0:
                final_velocity = (final_velocity / norm) * desired_speed
            else:
                final_velocity = np.zeros(2)
            drone.velocity = final_velocity
            drone.position += drone.velocity
            drone.constrain_to_bounds(WIDTH, HEIGHT)
            drone.sync_from_position()

            # Use AttackManager for attack logic
            AttackManager.handle_attack(drone, self)

            # State management for return to base, landing, etc.
            StateManager.update_drone_state(drone, self)
        
        # Use AlertManager for alerts
        from DroneSystem.Controllers.AlertManager import AlertManager
        AlertManager.handle_alerts(self.drones, self.alert_system)
        self.mission_complete_alerted = AlertManager.handle_mission_complete(
            self.drones, self.alert_system, self.mission_complete_alerted
        )
        
        # Check if we're in escort mode
        if hasattr(self.sim_modes, 'current_mode') and self.sim_modes.current_mode == Modes.ESCORT:
            self.update_escort_formation()
        
        return {'target_destroyed': False}

    def update_escort_formation(self):
        """Delegate escort formation logic to EscortFormationManager."""
        from DroneSystem.Controllers.EscortFormationManager import EscortFormationManager
        EscortFormationManager.update_escort_formation(
            self.drones,
            self.target,
            self.get_target_position
        )
