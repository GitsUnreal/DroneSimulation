"""Reconnaissance simulation mode handler"""
from .BaseHandler import BaseHandler

class ReconModeHandler(BaseHandler):
    """Handler for reconnaissance mode"""
    
    def __init__(self):
        super().__init__()
        self.name = "Reconnaissance"
    
    def update(self, drones, targets, dt):
        """Update drones in recon mode"""
        # Recon behavior - patrol and observe, don't attack
        for drone in drones:
            if drone.alive:
                self._patrol_behavior(drone, dt)
    
    def on_enter(self):
        """Enter recon mode"""
        print("Entering Reconnaissance mode")
    
    def on_exit(self):
        """Exit recon mode"""
        print("Exiting Reconnaissance mode")
    
    def _patrol_behavior(self, drone, dt):
        """Make drone patrol the area"""
        # Simple patrol pattern
        import math
        import time
        
        # Circular patrol pattern
        t = time.time() * 0.5  # Slow movement
        radius = 100
        center_x, center_y = 400, 300
        
        target_x = center_x + radius * math.cos(t)
        target_y = center_y + radius * math.sin(t)
        
        dx = target_x - drone.x
        dy = target_y - drone.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance > 5:
            drone.velocity[0] = (dx / distance) * 1.5
            drone.velocity[1] = (dy / distance) * 1.5