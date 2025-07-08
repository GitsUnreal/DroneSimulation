"""Base entity class"""
import numpy as np
from abc import ABC, abstractmethod

class Entity(ABC):
    def __init__(self, position, entity_id):
        self.position = np.array(position, dtype=float)
        self.entity_id = entity_id
        self.alive = True
    
    @abstractmethod
    def update(self, dt):
        pass
    
    def destroy(self):
        self.alive = False