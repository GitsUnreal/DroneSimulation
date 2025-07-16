import numpy as np
from ..Movement.Behaviors.Boids import Boids
from ..Movement.Navigation.ObstacleAvoidance import OAI
from ..Movement.Navigation.Pathfinding import Pathfinding

class MovementController:
    def __init__(self, drones, obstacles, base):
        self.drones = drones
        self.obstacles = obstacles
        self.base = base
        
        # Initialize movement systems
        self.boids = Boids(drones)
        self.oai = OAI(drones, obstacles, 20)
        self.pathfinding = Pathfinding(self.oai)
        
        # Movement parameters
        self.WIDTH, self.HEIGHT = 1080, 720
    
    def update_drone_movement(self, drone, behavior, simulation_step):
        """Update a single drone's movement based on its current behavior"""
        # Get movement forces based on behavior type
        if behavior['type'] == 'search':
            target_force = self._get_search_force(drone, behavior, simulation_step)
        elif behavior['type'] == 'attack':
            target_force = self._get_attack_force(drone, behavior['target'])
        elif behavior['type'] == 'return':
            target_force = self._get_return_force(drone)
        else:
            target_force = np.zeros(2)
        
        # Calculate boids forces
        movement_params = behavior.get('movement_params', {})
        sep = self.boids.compute_separation(drone) * movement_params.get('separation_weight', 2.0)
        ali = self.boids.compute_alignment(drone) * movement_params.get('alignment_weight', 0.1)
        coh = self.boids.compute_cohesion(drone) * movement_params.get('cohesion_weight', 0.1)
        
        # Obstacle avoidance
        avoidance_force = self._calculate_obstacle_avoidance(drone)
        
        # Handle pathfinding if needed
        if behavior.get('use_pathfinding', False):
            self._handle_pathfinding(drone, behavior['target_position'])
        
        # Combine all forces and apply movement
        self._apply_movement_forces(drone, target_force, sep, ali, coh, avoidance_force)
    
    def _get_search_force(self, drone, behavior, simulation_step):
        """Generate force for search behavior"""
        if not hasattr(drone, 'search_waypoint'):
            # Generate search waypoint based on pattern
            pattern = behavior.get('pattern', 'spiral')
            if pattern == 'spiral':
                drone.search_waypoint = self._generate_spiral_waypoint(drone, simulation_step)
            elif pattern == 'sweep':
                drone.search_waypoint = self._generate_sweep_waypoint(drone, simulation_step)
        
        target_vec = drone.search_waypoint - drone.position
        distance = np.linalg.norm(target_vec)
        return (target_vec / (distance + 1e-6)) * 1.5 if distance > 5 else np.zeros(2)
    
    def _generate_spiral_waypoint(self, drone, simulation_step):
        """Generate spiral search pattern waypoint"""
        center_screen = np.array([self.WIDTH / 2, self.HEIGHT / 2])
        angle = (drone.drone_id * 45 + simulation_step * 4) % 360
        radius = 50 + simulation_step * 2 + (drone.drone_id * 10)
        return center_screen + np.array([
            radius * np.cos(np.deg2rad(angle)),
            radius * np.sin(np.deg2rad(angle))
        ])
    
    # ... other movement methods