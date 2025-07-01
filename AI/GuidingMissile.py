from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPainter, QColor
import numpy as np
from AI.ObstacleAvoidance import OAI

class GuidingMissile:
    """
    GuidingMissile class to manage the pathfinding and obstacle avoidance for missiles.
    This class uses a grid-based approach to find paths while avoiding obstacles.
    It supports both individual missiles pathfinding and collective pathfinding for all missiles.
    """
    
    def __init__(self, drone, target, oai, grid):
        """
        Initialize the GuidingMissile with target, drones, obstacles, and cell size.
        """
        self.drone = drone
        self.target = target
        self.oai = oai
        self.grid = grid
        self.oai.add_neighbors(self.grid)

    def shootMissile(self, start, goal, requesting_drone=None):
        """
        Shoot a missile from start to goal while avoiding obstacles.
        :param start: The starting position as a (x, y) tuple.
        :param goal: The goal position as a (x, y) tuple.
        :param requesting_drone: The drone requesting the path (for individual pathfinding).
        :return: True if missile was successfully created, False otherwise.
        """
        # Check if drone can fire missile
        if not self.drone.can_fire_missile():
            print(f"Drone {self.drone.id}: Cannot fire missile - limit reached or drone destroyed")
            return False
        
        # Find path for the missile
        path = self.oai.find_path(self.grid, start, goal, requesting_drone)
        
        # Create missile with complete data
        missile_data = {
            'position': [float(start[0]), float(start[1])],  # Current position (mutable)
            'target': goal,
            'path': path if path else [],
            'path_index': 0,
            'active': True,
            'speed': 3.0,
            'missile_id': f"drone_{self.drone.id}_missile_{self.drone.missiles_fired + 1}"
        }
        
        # Store missile for later painting and updating by MainWindow
        if not hasattr(self.drone, 'missiles'):
            self.drone.missiles = []
        self.drone.missiles.append(missile_data)
        
        print(f"Missile launched from {start} to {goal} with {len(missile_data['path'])} waypoints")
        
        return True