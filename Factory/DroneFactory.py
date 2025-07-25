"""
DroneFactory.py
Factory for creating drones with various configurations.
"""
import numpy as np
from DroneSystem.Core.Drone import Drone, DroneMovementConfig, DroneMovementMode

class DroneFactory:
    @staticmethod
    def create_drone(position, velocity, drone_id, movement_mode=None):
        drone = Drone(position, velocity, drone_id)
        if movement_mode:
            if isinstance(movement_mode, DroneMovementMode):
                drone.movement_config = movement_mode.value
            elif isinstance(movement_mode, dict):
                drone.movement_config = DroneMovementConfig(**movement_mode)
        return drone

    @staticmethod
    def create_random_drone(drone_id=1, bounds=None):
        if bounds is None:
            bounds = {'min_x': 0, 'max_x': 1000, 'min_y': 0, 'max_y': 1000}
        position = [
            np.random.uniform(bounds['min_x'], bounds['max_x']),
            np.random.uniform(bounds['min_y'], bounds['max_y'])
        ]
        velocity = [np.random.uniform(-1, 1), np.random.uniform(-1, 1)]
        movement_mode = np.random.choice(list(DroneMovementMode))
        return DroneFactory.create_drone(position, velocity, drone_id, movement_mode)

    @staticmethod
    def create_drones(count=1, bounds=None):
        return [DroneFactory.create_random_drone(drone_id=i+1, bounds=bounds) for i in range(count)]
