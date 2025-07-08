"""Search and destroy simulation mode handler"""
from .BaseHandler import BaseHandler

class SearchDestroyModeHandler(BaseHandler):
    """Handler for search and destroy mode"""
    
    def __init__(self):
        super().__init__()
        self.name = "Search & Destroy"
    
    def update(self, drones, targets, dt):
        """Update drones in search and destroy mode"""
        # Aggressive behavior - actively hunt targets
        for drone in drones:
            if drone.alive:
                self._search_and_destroy(drone, targets, dt)
    
    def on_enter(self):
        """Enter search and destroy mode"""
        print("Entering Search & Destroy mode")
    
    def on_exit(self):
        """Exit search and destroy mode"""
        print("Exiting Search & Destroy mode")
    
    def _search_and_destroy(self, drone, targets, dt):
        """Aggressive target seeking behavior"""
        if not targets:
            # No targets, search pattern
            self._search_pattern(drone, dt)
            return
        
        # Find and aggressively pursue targets
        nearest_target = min(targets, key=lambda t: 
            ((t.x() - drone.x) ** 2 + (t.y() - drone.y) ** 2) ** 0.5
        )
        
        dx = nearest_target.x() - drone.x
        dy = nearest_target.y() - drone.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance > 0:
            # Faster, more aggressive movement
            speed = 3.0
            drone.velocity[0] = (dx / distance) * speed
            drone.velocity[1] = (dy / distance) * speed
    
    def _search_pattern(self, drone, dt):
        """Search pattern when no targets visible"""
        import math
        import time
        
        # Expanding spiral search
        t = time.time() * 2.0  # Faster search
        spiral_radius = 50 + (t % 200)
        
        target_x = 400 + spiral_radius * math.cos(t)
        target_y = 300 + spiral_radius * math.sin(t)
        
        dx = target_x - drone.x
        dy = target_y - drone.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance > 5:
            drone.velocity[0] = (dx / distance) * 2.5
            drone.velocity[1] = (dy / distance) * 2.5