

import numpy as np
from EnemySystem.EnemyBase import EnemyBase

class AntiDrone(EnemyBase):
    def __init__(self, enemy_id, position=None, health=100, size=30):
        super().__init__(enemy_id, position, health, size)
        from EnemySystem.AntiDroneBehavior import AntiDroneBehavior
        self.behavior = AntiDroneBehavior(self)
        self.movement_pattern = "none"
        self.waypoints = []
        self.current_waypoint_index = 0
        self.speed = 2.0
        self.pattern_timer = 0
        self.direction = np.array([1.0, 0.0])
        self.bounds = {'min_x': 50, 'max_x': 800, 'min_y': 100, 'max_y': 500}

    def set_patrol(self, waypoints, speed=2.0):
        self.behavior.set_patrol(waypoints, speed)

    def set_random_patrol(self, speed=2.0):
        self.behavior.set_random_patrol(speed)

    def update_behavior(self, dt=1.0):
        self.behavior.update(dt)