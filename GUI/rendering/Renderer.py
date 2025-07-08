"""Base renderer class"""
from abc import ABC, abstractmethod

class Renderer(ABC):
    """Base class for all renderers"""
    
    def __init__(self):
        self.enabled = True
        
    @abstractmethod
    def render(self, painter, objects):
        """Render objects using the painter"""
        pass
    
    def set_enabled(self, enabled):
        """Enable or disable this renderer"""
        self.enabled = enabled
    
    def is_enabled(self):
        """Check if renderer is enabled"""
        return self.enabled