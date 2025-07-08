"""Obstacle implementation for the simulation"""

class Obstacle:
    """Static obstacle in the simulation environment"""
    
    def __init__(self, x, y, width, height):
        self.x_pos = x
        self.y_pos = y
        self.width_val = width
        self.height_val = height
        self.color = (139, 69, 19)  # Brown color
    
    def x(self):
        """Get x position"""
        return self.x_pos
    
    def y(self):
        """Get y position"""
        return self.y_pos
    
    def width(self):
        """Get width"""
        return self.width_val
    
    def height(self):
        """Get height"""
        return self.height_val
    
    def get_bounds(self):
        """Get obstacle bounds as (x, y, width, height)"""
        return (self.x(), self.y(), self.width(), self.height())
    
    def contains_point(self, x, y):
        """Check if point is inside obstacle"""
        return (self.x() <= x <= self.x() + self.width() and 
                self.y() <= y <= self.y() + self.height())