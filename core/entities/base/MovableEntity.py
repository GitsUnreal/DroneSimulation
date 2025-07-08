"""Base movable entity class"""
from .Entity import Entity
import numpy as np

class MovableEntity(Entity):
    def __init__(self, position, velocity, entity_id):
        super().__init__(position, entity_id)
        self.velocity = np.array(velocity, dtype=float)
    
    def constrain_to_bounds(self, width=1080, height=720):
        self.position[0] = max(10, min(self.position[0], width - 30))
        self.position[1] = max(10, min(self.position[1], height - 30))