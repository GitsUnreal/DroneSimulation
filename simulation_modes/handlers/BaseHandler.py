"""Base handler for simulation modes"""
from abc import ABC, abstractmethod

class BaseHandler(ABC):
    """Base class for all simulation mode handlers"""
    
    def __init__(self):
        self.name = "Base"
    
    @abstractmethod
    def update(self, drones, targets, dt):
        """Update logic for this mode"""
        pass
    
    @abstractmethod
    def on_enter(self):
        """Called when entering this mode"""
        pass
    
    @abstractmethod
    def on_exit(self):
        """Called when exiting this mode"""
        pass
    
    def get_description(self):
        """Get mode description"""
        return f"{self.name} simulation mode"