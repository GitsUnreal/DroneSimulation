from abc import ABC, abstractmethod

class ModeHandler(ABC):
    """Base interface for all simulation mode handlers"""
    
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def configure_drones(self, drones):
        """Configure drone behavior for this mode"""
        pass
    
    @abstractmethod
    def configure_target(self, target):
        """Configure target behavior for this mode"""
        pass
    
    @abstractmethod
    def get_movement_parameters(self):
        """Return movement parameters for this mode"""
        pass
    
    @abstractmethod
    def should_show_target(self):
        """Whether target should be visible in this mode"""
        pass
    
    def on_mode_start(self, sim_objects):
        """Called when mode starts - override if needed"""
        pass
    
    def on_mode_end(self, sim_objects):
        """Called when mode ends - override if needed"""
        pass