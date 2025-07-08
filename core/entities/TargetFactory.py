"""Factory for creating different types of targets"""
from .targets.Target import Target
from .targets.AntiDrone import AntiDrone
import random

class TargetFactory:
    """Factory for creating targets"""
    
    @staticmethod
    def create_random_target(obstacles=None):
        """Create a random target"""
        # Simple target creation
        x = random.randint(100, 900)
        y = random.randint(100, 600)
        return Target(x, y, 30)
    
    @staticmethod
    def create_anti_drone(x, y):
        """Create an anti-drone target"""
        return AntiDrone(x, y)