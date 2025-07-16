import random
import numpy as np
from PyQt5.QtCore import QRect
from DroneSystem.Movement.Drone import Drone
from DroneSystem.MainController import MainController
from GUI.Objects.Obstacle import Obstacle
from Factory.TargetFactory import TargetFactory
from Utils.PositionUtils import PositionUtils
from Utils.DroneUtils import DroneUtils
from Config.SimulationConfig import SimulationConfig

class SimulationManager:
    def __init__(self):
        self.drones = []
        self.obstacles = []
        self.target = None
        self.base = None
        self.movement_controller = None

    def init_default_simulation(self, num_drones=None):
        """Initialize simulation with default parameters"""
        if num_drones is None:
            num_drones = SimulationConfig.DEFAULT_DRONES
        
        self.init_simulation(num_drones)

    def init_simulation(self, num_drones=2):
        """Initialize simulation objects and controller."""
        # Create base first
        self.base = QRect(*SimulationConfig.BASE_POSITION, SimulationConfig.BASE_SIZE, SimulationConfig.BASE_SIZE)
        base_center = (
            self.base.x() + self.base.width() / 2,
            self.base.y() + self.base.height() / 2
        )
        
        # Create drones around base
        self.drones = []
        spawn_radius = SimulationConfig.SPAWN_RADIUS
        
        for i in range(num_drones):
            # Position drones in a circle around base
            angle = (2 * np.pi * i) / num_drones
            spawn_x = base_center[0] + spawn_radius * np.cos(angle)
            spawn_y = base_center[1] + spawn_radius * np.sin(angle)
            
            drone = Drone(
                position=[spawn_x, spawn_y],
                velocity=[0, 0],  # Start stationary
                drone_id=i
            )
            self.drones.append(drone)

        # Create obstacles
        self.obstacles = [
            Obstacle(200, 150, 100, 50),
            Obstacle(350, 300, 100, 50),
            Obstacle(600, 200, 80, 60),
            Obstacle(150, 400, 120, 40),
        ]
        
        # Use factory to create target
        self.target = TargetFactory.create_random_target(self.obstacles)

    def check_target_status(self):
        """Check if target has been destroyed"""
        if self.target and hasattr(self.target, 'destroyed') and self.target.destroyed:
            return True
        if self.target and hasattr(self.target, 'is_destroyed') and self.target.is_destroyed():
            return True
        return False

    def reset_simulation(self):
        """Reset all drones and create new target"""
        base_center = (
            self.base.x() + self.base.width() / 2,
            self.base.y() + self.base.height() / 2
        )
        
        # Reset drones to positions around base
        spawn_radius = SimulationConfig.SPAWN_RADIUS
        for i, drone in enumerate(self.drones):
            angle = (2 * np.pi * i) / len(self.drones)
            spawn_x = base_center[0] + spawn_radius * np.cos(angle)
            spawn_y = base_center[1] + spawn_radius * np.sin(angle)
            
            DroneUtils.reset_drone_to_position(drone, (spawn_x, spawn_y))

        # Reset target
        if self.target:
            if hasattr(self.target, 'destroyed'):
                self.target.destroyed = False
            if hasattr(self.target, 'spotted_by_radar'):
                self.target.spotted_by_radar = False

        # Create new target using factory
        self.target = TargetFactory.create_random_target(self.obstacles)

    def get_active_drones(self):
        """Get drones that are actively participating in simulation"""
        return DroneUtils.get_active_drones(self.drones)

    def get_landed_drones(self):
        """Get drones that have landed at base"""
        return DroneUtils.get_landed_drones(self.drones)

    def reactivate_all_landed_drones(self):
        """Reactivate all landed drones for a new mission"""
        landed_drones = self.get_landed_drones()
        for drone in landed_drones:
            if hasattr(drone, 'reactivate_from_base'):
                drone.reactivate_from_base()
        
        if landed_drones:
            print(f"Reactivated {len(landed_drones)} drones from base")
        return len(landed_drones)

    def handle_collisions(self):
        """Handle drone collisions with obstacles and other drones - only for active drones"""
        active_drones = self.get_active_drones()
        
        for drone in active_drones:
            # Obstacle collisions
            for obs in self.obstacles:
                if hasattr(obs, 'contains') and obs.contains(int(drone.position[0]), int(drone.position[1])):
                    drone.destroy()
                    break

            # Drone-to-drone collisions (only with other active drones)
            for other in active_drones:
                if other is not drone:
                    dist = np.linalg.norm(drone.position - other.position)
                    if dist < 20:  # Collision radius
                        # Push drones apart
                        direction = drone.position - other.position
                        if np.linalg.norm(direction) > 0:
                            direction /= np.linalg.norm(direction)
                            drone.position += direction * 2
                            other.position -= direction * 2