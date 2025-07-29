import numpy as np
from typing import List, Any, Dict

class DroneUtils:
    """
    Utility functions for drone operations.
    """
    @staticmethod
    def reset_drone_to_position(drone: Any, position: List[float]) -> None:
        """
        Reset drone to a specific position.
        Args:
            drone (Any): Drone object.
            position (List[float]): Position to reset to.
        """
        drone.position = np.array(position, dtype=float)
        drone.velocity = np.array([0, 0], dtype=float)
        drone.alive = True
        drone.has_attacked = False
        drone.has_landed = False
        drone.current_path = []
        drone.current_waypoint_index = 0
        drone.missiles_fired = 0
        if hasattr(drone, 'missiles'):
            drone.missiles.clear()
        for attr in ['returning_to_base', '_destruction_alerted', '_missiles_alerted', '_landing_alerted']:
            if hasattr(drone, attr):
                delattr(drone, attr)
        if hasattr(drone, 'sync_from_position'):
            drone.sync_from_position()

    @staticmethod
    def get_active_drones(drones: List[Any]) -> List[Any]:
        """Get all drones that are actively participating in simulation."""
        return [drone for drone in drones if drone.alive and not (hasattr(drone, 'has_landed') and drone.has_landed)]

    @staticmethod
    def get_landed_drones(drones: List[Any]) -> List[Any]:
        """Get all drones that have landed at base."""
        return [drone for drone in drones if hasattr(drone, 'has_landed') and drone.has_landed]

    @staticmethod
    def get_destroyed_drones(drones: List[Any]) -> List[Any]:
        """Get all destroyed drones."""
        return [drone for drone in drones if not drone.alive]

    @staticmethod
    def get_drone_stats(drones: List[Any]) -> Dict[str, int]:
        """
        Get comprehensive drone statistics.
        Args:
            drones (List[Any]): List of drone objects.
        Returns:
            Dict[str, int]: Statistics dictionary.
        """
        active = DroneUtils.get_active_drones(drones)
        landed = DroneUtils.get_landed_drones(drones)
        destroyed = DroneUtils.get_destroyed_drones(drones)
        total_missiles_fired = sum(drone.missiles_fired for drone in drones)
        total_missiles_available = sum(getattr(drone, 'max_missiles', 0) for drone in drones)
        return {
            'total': len(drones),
            'active': len(active),
            'landed': len(landed),
            'destroyed': len(destroyed),
            'missiles_fired': total_missiles_fired,
            'missiles_available': total_missiles_available,
            'drones_attacked': sum(1 for drone in drones if getattr(drone, 'has_attacked', False))
        }