import random
import numpy as np

class PositionUtils:
    """Utility functions for position calculations and validation"""
    
    @staticmethod
    def is_position_valid(position, obstacles, width=20, height=20, margin=10):
        """Check if a position is valid (not intersecting obstacles)"""
        x, y = position
        
        # Check bounds
        if x < margin or y < margin or x + width > 1080 - margin or y + height > 720 - margin:
            return False
        
        # Check obstacles
        for obs in obstacles:
            obs_x = obs.x() if hasattr(obs, 'x') else obs.position[0]
            obs_y = obs.y() if hasattr(obs, 'y') else obs.position[1]
            obs_w = obs.width() if hasattr(obs, 'width') else obs.width
            obs_h = obs.height() if hasattr(obs, 'height') else obs.height
            
            # Check if rectangles overlap with margin
            if (x < obs_x + obs_w + margin and 
                x + width > obs_x - margin and
                y < obs_y + obs_h + margin and 
                y + height > obs_y - margin):
                return False
        
        return True
    
    @staticmethod
    def find_valid_position(obstacles, width=20, height=20, margin=30, max_attempts=100):
        """Find a valid position that doesn't intersect with obstacles"""
        for _ in range(max_attempts):
            x = random.randint(margin, 1080 - width - margin)
            y = random.randint(margin, 720 - height - margin)
            
            if PositionUtils.is_position_valid((x, y), obstacles, width, height, margin):
                return (x, y)
        
        # Fallback: return a safe position in top-left corner
        return (100, 100)
    
    @staticmethod
    def distance_between_points(point1, point2):
        """Calculate distance between two points"""
        return np.linalg.norm(np.array(point1) - np.array(point2))
    
    @staticmethod
    def find_nearest_valid_position(target_pos, obstacles, width=20, height=20):
        """Find the nearest valid position to a target position"""
        if PositionUtils.is_position_valid(target_pos, obstacles, width, height):
            return target_pos
        
        # Search in expanding circles
        for radius in range(10, 200, 10):
            for angle in range(0, 360, 30):
                angle_rad = np.radians(angle)
                test_x = target_pos[0] + radius * np.cos(angle_rad)
                test_y = target_pos[1] + radius * np.sin(angle_rad)
                test_pos = (test_x, test_y)
                
                if PositionUtils.is_position_valid(test_pos, obstacles, width, height):
                    return test_pos
        
        # Fallback
        return PositionUtils.find_valid_position(obstacles, width, height)