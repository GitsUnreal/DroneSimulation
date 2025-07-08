# drone_system/movement/MovementController.py
import numpy as np
from .Boids import Boids

class MovementController:
    """Handles all drone movement logic"""
    
    def __init__(self, drones, obstacles, pathfinder):
        self.drones = drones
        self.obstacles = obstacles
        self.pathfinder = pathfinder
        self.boids = Boids(drones)
    
    def update_drone_movement(self, drone, target_position, dt):
        """Update single drone movement"""
        if not drone.is_active():
            return
        
        # Calculate forces
        forces = self._calculate_forces(drone, target_position)
        
        # Apply movement
        drone.velocity += forces['total'] * dt
        drone.velocity = self._limit_velocity(drone.velocity)
        drone.update(dt)
    
    def _calculate_forces(self, drone, target_position):
        """Calculate all forces acting on drone"""
        target_force = self._calculate_target_force(drone, target_position)
        avoidance_force = self._calculate_avoidance_force(drone)
        boids_forces = self._calculate_boids_forces(drone)
        
        total_force = target_force + avoidance_force + boids_forces
        
        return {
            'target': target_force,
            'avoidance': avoidance_force,
            'boids': boids_forces,
            'total': total_force
        }
    
    def _calculate_target_force(self, drone, target_position):
        """Calculate force towards target"""
        direction = target_position - drone.position
        distance = np.linalg.norm(direction)
        
        if distance > 5:
            return (direction / distance) * 1.5
        return np.zeros(2)
    
    def _calculate_avoidance_force(self, drone):
        """Calculate obstacle avoidance force"""
        avoidance_force = np.zeros(2)
        
        for obstacle in self.obstacles:
            obs_center = np.array([
                obstacle.x() + obstacle.width()/2, 
                obstacle.y() + obstacle.height()/2
            ])
            to_obs = obs_center - drone.position
            distance = np.linalg.norm(to_obs)
            
            if distance < 50 and distance > 0:
                avoidance_force += -(to_obs / distance) * (100 / (distance + 1))
        
        return avoidance_force
    
    def _calculate_boids_forces(self, drone):
        """Calculate boids flocking forces"""
        return (self.boids.compute_separation(drone) * 2.0 + 
                self.boids.compute_alignment(drone) * 0.1 + 
                self.boids.compute_cohesion(drone) * 0.1)
    
    def _limit_velocity(self, velocity, max_speed=3.0):
        """Limit velocity to maximum speed"""
        speed = np.linalg.norm(velocity)
        if speed > max_speed:
            return velocity * (max_speed / speed)
        return velocity