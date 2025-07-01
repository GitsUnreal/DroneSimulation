import numpy as np
from .GuidingMissile import GuidingMissile

class Drone:
    def __init__(self, position, velocity, drone_id):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.x, self.y = self.position
        self.alive = True
        self.drone_id = drone_id
        self.has_attacked = False

        self.max_missiles = 2
        self.missiles_fired = 0
        self.current_path = []
        self.current_waypoint_index = 0

    def update_position_sync(self):
        self.position[0], self.position[1] = self.x, self.y

    def sync_from_position(self):
        self.x, self.y = self.position

    def constrain_to_bounds(self, width=1080, height=720):
        self.position[0] = max(10, min(self.position[0], width - 30))
        self.position[1] = max(10, min(self.position[1], height - 30))
        self.sync_from_position()

    def destroy(self):
        self.alive = False

    def is_destroyed(self):
        return not self.alive

    def can_fire_missile(self):
        return self.alive and self.missiles_fired < self.max_missiles

    def attack(self, drone, target, oai, grid):
        if not self.can_fire_missile():
            print(f"Drone {self.drone_id}: Cannot fire missile ({self.missiles_fired}/{self.max_missiles})")
            return

        start = tuple(self.position)
        target_pos = (target.x(), target.y())

        self.guiding_missile = GuidingMissile(drone, target, oai, grid)
        if self.guiding_missile.shoot_missile(start, target_pos):
            self.missiles_fired += 1
            print(f"Drone {self.drone_id}: Fired missile ({self.missiles_fired}/{self.max_missiles})")

    def reset_missiles(self):
        self.missiles_fired = 0
