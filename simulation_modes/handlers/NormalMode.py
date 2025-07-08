"""Normal simulation mode handler"""
from .BaseHandler import BaseHandler

class NormalModeHandler(BaseHandler):
    """Handler for normal simulation mode"""
    
    def __init__(self):
        super().__init__()
        self.name = "Normal"
    
    def update(self, drones, targets, dt):
        """Update drones in normal mode"""
        # Standard drone behavior - move toward targets and attack
        for drone in drones:
            if not drone.has_attacked and drone.alive:
                # Move toward nearest target
                self._move_toward_target(drone, targets, dt)
    
    def on_enter(self):
        """Enter normal mode"""
        print("Entering Normal simulation mode")
    
    def on_exit(self):
        """Exit normal mode"""
        print("Exiting Normal simulation mode")
    
    def _move_toward_target(self, drone, targets, dt):
        """Move drone toward nearest target"""
        if not targets:
            return
        
        # Find nearest target
        nearest_target = min(targets, key=lambda t: 
            ((t.x() - drone.x) ** 2 + (t.y() - drone.y) ** 2) ** 0.5
        )
        
        # Move toward target (simplified)
        dx = nearest_target.x() - drone.x
        dy = nearest_target.y() - drone.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance > 0:
            drone.velocity[0] = (dx / distance) * 2.0
            drone.velocity[1] = (dy / distance) * 2.0