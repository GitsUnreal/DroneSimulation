from PyQt5.QtCore import QRect

class Obstacle:
    def __init__(self, x, y, width, height, active=True, is_hidden=True):  # Keep hidden by default
        self.rect = QRect(x, y, width, height)
        self.active = active
        self.is_hidden = is_hidden  # Start hidden for radar testing

    def is_spotted(self, radar_position, radar_radius):
        """Check if the obstacle is within the radar's detection range."""
        # Mark as detected/visible
        self.is_hidden = False
        #print(f"Obstacle at ({self.x()}, {self.y()}) detected by radar!")
    
    # Add convenience methods to match QRect interface
    def x(self):
        return self.rect.x()
    
    def y(self):
        return self.rect.y()
    
    def width(self):
        return self.rect.width()
    
    def height(self):
        return self.rect.height()
    
    def contains(self, x, y):
        return self.rect.contains(x, y)
