import numpy as np

class DroneUtils:
    @staticmethod
    def get_active_drones(drones):
        """Get drones that are actively participating in simulation"""
        return [drone for drone in drones if drone.alive and not (hasattr(drone, 'has_landed') and drone.has_landed)]

    @staticmethod
    def get_landed_drones(drones):
        """Get drones that have landed at base"""
        return [drone for drone in drones if hasattr(drone, 'has_landed') and drone.has_landed]

    @staticmethod
    def get_destroyed_drones(drones):
        """Get drones that have been destroyed"""
        return [drone for drone in drones if not drone.alive]

    @staticmethod
    def count_active_missiles(drones):
        """Count total active missiles across all drones"""
        total = 0
        for drone in drones:
            if hasattr(drone, 'missiles'):
                total += len([m for m in drone.missiles if m['active']])
        return total

    @staticmethod
    def reset_drone_to_position(drone, position):
        """Reset a drone to a specific position with clean state"""
        drone.position = np.array(position, dtype=float)
        drone.x, drone.y = position[0], position[1]
        drone.velocity = np.zeros(2)
        drone.alive = True
        drone.has_attacked = False
        drone.has_landed = False
        
        if hasattr(drone, 'returning_to_base'):
            drone.returning_to_base = False

        drone.reset_missiles()
        drone.current_path = []
        drone.current_waypoint_index = 0
        if hasattr(drone, 'current_path_timer'):
            drone.current_path_timer = 0