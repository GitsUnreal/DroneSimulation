"""Drone manager for coordinating multiple drones"""
from .Drone import Drone
from typing import List
import numpy as np

class DroneManager:
    """Manages multiple drones in the simulation"""
    
    def __init__(self):
        self.drones: List[Drone] = []
        self.active_drones: List[Drone] = []
        self.landed_drones: List[Drone] = []
    
    def add_drone(self, drone: Drone):
        """Add a drone to management"""
        self.drones.append(drone)
        self.active_drones.append(drone)
    
    def remove_drone(self, drone_id: int):
        """Remove a drone by ID"""
        self.drones = [d for d in self.drones if d.drone_id != drone_id]
        self.active_drones = [d for d in self.active_drones if d.drone_id != drone_id]
        self.landed_drones = [d for d in self.landed_drones if d.drone_id != drone_id]
    
    def get_active_drones(self) -> List[Drone]:
        """Get all active (non-landed) drones"""
        return [d for d in self.drones if d.alive and not (hasattr(d, 'has_landed') and d.has_landed)]
    
    def get_landed_drones(self) -> List[Drone]:
        """Get all landed drones"""
        return [d for d in self.drones if hasattr(d, 'has_landed') and d.has_landed]
    
    def update_all_drones(self, dt: float):
        """Update all managed drones"""
        for drone in self.get_active_drones():
            drone.update(dt)
    
    def get_drone_by_id(self, drone_id: int) -> Drone:
        """Get drone by ID"""
        for drone in self.drones:
            if drone.drone_id == drone_id:
                return drone
        return None
    
    def get_drone_count(self) -> dict:
        """Get count of drones by status"""
        return {
            'total': len(self.drones),
            'active': len(self.get_active_drones()),
            'landed': len(self.get_landed_drones()),
            'destroyed': len([d for d in self.drones if not d.alive])
        }