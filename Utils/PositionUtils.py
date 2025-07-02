import random

class PositionUtils:
    @staticmethod
    def is_position_valid(position, obstacles, width=20, height=20, margin=10):
        """Check if a position is valid (not inside obstacles with margin)"""
        x, y = position
        
        # Check bounds
        if x < 50 or x > 1000 or y < 100 or y > 600:
            return False
        
        # Check collision with obstacles
        for obstacle in obstacles:
            # Get obstacle rectangle
            if hasattr(obstacle, 'rect'):
                obs_rect = obstacle.rect
            else:
                obs_rect = obstacle
            
            # Add margin around obstacles
            if (obs_rect.x() - margin <= x <= obs_rect.x() + obs_rect.width() + margin and
                obs_rect.y() - margin <= y <= obs_rect.y() + obs_rect.height() + margin):
                return False
        
        return True

    @staticmethod
    def find_valid_position(obstacles, width=20, height=20, margin=10, max_attempts=50):
        """Find a valid spawn position that doesn't overlap with obstacles"""
        for _ in range(max_attempts):
            x = random.randint(50, 1000)
            y = random.randint(100, 600)
            
            if PositionUtils.is_position_valid((x, y), obstacles, width, height, margin):
                return (x, y)
        
        # Fallback to safe positions if no valid position found
        safe_positions = [
            (75, 125), (100, 150), (125, 175), (150, 200),  # Top-left area
            (900, 500), (850, 450), (800, 400), (750, 350)  # Bottom-right area
        ]
        
        for pos in safe_positions:
            if PositionUtils.is_position_valid(pos, obstacles, width, height, margin):
                return pos
        
        # Last resort - return a position far from obstacles
        return (75, 125)