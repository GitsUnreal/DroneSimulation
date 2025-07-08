"""Common helper utilities for drone operations"""
import numpy as np
import math

class DroneUtils:
    """Utility functions for drone calculations and operations"""
    
    @staticmethod
    def calculate_distance(pos1, pos2):
        """Calculate distance between two positions"""
        return np.linalg.norm(np.array(pos1) - np.array(pos2))
    
    @staticmethod
    def normalize_vector(vector):
        """Normalize a vector to unit length"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm
    
    @staticmethod
    def clamp(value, min_val, max_val):
        """Clamp value between min and max"""
        return max(min_val, min(value, max_val))
    
    @staticmethod
    def angle_to_vector(angle):
        """Convert angle to unit vector"""
        return np.array([math.cos(angle), math.sin(angle)])
    
    @staticmethod
    def vector_to_angle(vector):
        """Convert vector to angle"""
        return math.atan2(vector[1], vector[0])