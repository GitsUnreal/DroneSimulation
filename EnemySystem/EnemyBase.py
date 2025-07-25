import numpy as np

class EnemyBase:
    def __init__(self, enemy_id, position=None, health=100, size=30):
        self.enemy_id = enemy_id
        self.position = np.array(position, dtype=float) if position is not None else np.array([400.0, 300.0], dtype=float)
        self.health = health
        self.size = size
        self.alive = True
        self.velocity = np.zeros(2)
        self.destroyed = False

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.destroyed = True
            self.alive = False

    def is_destroyed(self):
        return self.destroyed

    def update(self, dt=1.0):
        pass  # To be implemented by subclasses or behaviors
