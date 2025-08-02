
import random
import numpy as np
from typing import List, Any, Tuple, Optional

class PositionUtils:
    """
    Utility functions for position calculations and validation.
    """
    @staticmethod
    def is_position_valid(position: Tuple[float, float], obstacles: List[Any], width: int = 20, height: int = 20, margin: int = 10) -> bool:
        """
        Check if a position is valid (not intersecting obstacles).
        Args:
            position (Tuple[float, float]): Position to check.
            obstacles (List[Any]): List of obstacles.
            width (int): Width of object.
            height (int): Height of object.
            margin (int): Margin for bounds.
        Returns:
            bool: True if valid, False otherwise.
        """
        x, y = position
        if x < margin or y < margin or x + width > 1080 - margin or y + height > 720 - margin:
            return False
        for obs in obstacles:
            obs_x = obs.x() if hasattr(obs, 'x') else obs.position[0]
            obs_y = obs.y() if hasattr(obs, 'y') else obs.position[1]
            obs_w = obs.width() if hasattr(obs, 'width') else obs.width
            obs_h = obs.height() if hasattr(obs, 'height') else obs.height
            if (x < obs_x + obs_w + margin and
                x + width > obs_x - margin and
                y < obs_y + obs_h + margin and
                y + height > obs_y - margin):
                return False
        return True

    @staticmethod
    def find_valid_position(obstacles: List[Any], width: int = 20, height: int = 20, margin: int = 30, max_attempts: int = 100) -> Optional[Tuple[int, int]]:
        """
        Find a valid position that doesn't intersect with obstacles.
        Args:
            obstacles (List[Any]): List of obstacles.
            width (int): Width of object.
            height (int): Height of object.
            margin (int): Margin for bounds.
            max_attempts (int): Maximum attempts.
        Returns:
            Optional[Tuple[int, int]]: Valid position or None.
        """
        for _ in range(max_attempts):
            x = random.randint(margin, 1080 - width - margin)
            y = random.randint(margin, 720 - height - margin)
            if PositionUtils.is_position_valid((x, y), obstacles, width, height, margin):
                return (x, y)
        return None

    @staticmethod
    def distance_between_points(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        Calculate distance between two points.
        Args:
            point1 (Tuple[float, float]): First point.
            point2 (Tuple[float, float]): Second point.
        Returns:
            float: Distance.
        """
        return float(np.linalg.norm(np.array(point1) - np.array(point2)))

    @staticmethod
    def find_nearest_valid_position(target_pos: Tuple[float, float], obstacles: List[Any], width: int = 20, height: int = 20) -> Optional[Tuple[float, float]]:
        """
        Find the nearest valid position to a target position.
        Args:
            target_pos (Tuple[float, float]): Target position.
            obstacles (List[Any]): List of obstacles.
            width (int): Width of object.
            height (int): Height of object.
        Returns:
            Optional[Tuple[float, float]]: Valid position or None.
        """
        if PositionUtils.is_position_valid(target_pos, obstacles, width, height):
            return target_pos
        for radius in range(10, 200, 10):
            for angle in range(0, 360, 30):
                angle_rad = np.radians(angle)
                test_x = target_pos[0] + radius * np.cos(angle_rad)
                test_y = target_pos[1] + radius * np.sin(angle_rad)
                test_pos = (test_x, test_y)
                if PositionUtils.is_position_valid(test_pos, obstacles, width, height):
                    return test_pos
        return PositionUtils.find_valid_position(obstacles, width, height)