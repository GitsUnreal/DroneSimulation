import numpy as np
from typing import List, Dict, Tuple
from enum import Enum

class SearchPattern(Enum):
    SPIRAL = "spiral"
    GRID = "grid"
    SWEEP = "sweep"
    RANDOM_WALK = "random_walk"
    PERIMETER = "perimeter"

class PatternGenerator:
    def __init__(self, width=1080, height=720):
        self.width = width
        self.height = height
        self.center = np.array([width/2, height/2])
    
    def generate_search_pattern(self, pattern_type: SearchPattern, drone, simulation_step: int, **kwargs) -> np.ndarray:
        """Generate search waypoint based on pattern type"""
        if pattern_type == SearchPattern.SPIRAL:
            return self.generate_spiral_pattern(drone, simulation_step, **kwargs)
        elif pattern_type == SearchPattern.GRID:
            return self.generate_grid_pattern(drone, simulation_step, **kwargs)
        elif pattern_type == SearchPattern.SWEEP:
            return self.generate_sweep_pattern(drone, simulation_step, **kwargs)
        elif pattern_type == SearchPattern.RANDOM_WALK:
            return self.generate_random_walk_pattern(drone, simulation_step, **kwargs)
        elif pattern_type == SearchPattern.PERIMETER:
            return self.generate_perimeter_pattern(drone, simulation_step, **kwargs)
        else:
            return self.generate_spiral_pattern(drone, simulation_step, **kwargs)
    
    def generate_spiral_pattern(self, drone, simulation_step: int, center=None, speed_multiplier=1.0) -> np.ndarray:
        """Generate expanding spiral search pattern"""
        if center is None:
            center = self.center
        
        angle = (drone.drone_id * 45 + simulation_step * 4 * speed_multiplier) % 360
        radius = 50 + simulation_step * 2 + (drone.drone_id * 15)
        
        # Prevent spiral from going off-screen
        max_radius = min(self.width, self.height) / 3
        radius = min(radius, max_radius)
        
        waypoint = center + np.array([
            radius * np.cos(np.deg2rad(angle)),
            radius * np.sin(np.deg2rad(angle))
        ])
        
        return self._clamp_to_bounds(waypoint)
    
    def generate_grid_pattern(self, drone, simulation_step: int, grid_size=100) -> np.ndarray:
        """Generate systematic grid search pattern"""
        # Calculate grid dimensions
        cols = self.width // grid_size
        rows = self.height // grid_size
        
        # Calculate current grid cell based on simulation step and drone ID
        total_cells = cols * rows
        cell_index = (simulation_step + drone.drone_id * 10) % total_cells
        
        col = cell_index % cols
        row = cell_index // cols
        
        waypoint = np.array([
            col * grid_size + grid_size/2,
            row * grid_size + grid_size/2
        ])
        
        return self._clamp_to_bounds(waypoint)
    
    def generate_sweep_pattern(self, drone, simulation_step: int, total_drones=None) -> np.ndarray:
        """Generate horizontal sweep pattern"""
        if total_drones is None:
            total_drones = 5  # Default assumption
        
        # Assign each drone a horizontal lane
        lane_height = self.height / (total_drones + 1)
        y_position = lane_height * (drone.drone_id + 1)
        
        # Sweep back and forth
        sweep_speed = 3
        x_position = (simulation_step * sweep_speed) % (self.width * 2)
        if x_position > self.width:
            x_position = self.width * 2 - x_position  # Reverse direction
        
        return np.array([x_position, y_position])
    
    def generate_random_walk_pattern(self, drone, simulation_step: int, step_size=50) -> np.ndarray:
        """Generate controlled random walk pattern"""
        # Use drone ID and simulation step as seed for reproducible randomness
        np.random.seed(drone.drone_id * 1000 + simulation_step // 10)
        
        # Get current position or use center as starting point
        current_pos = getattr(drone, 'last_search_pos', self.center)
        
        # Generate random direction
        angle = np.random.uniform(0, 2 * np.pi)
        step = np.array([
            step_size * np.cos(angle),
            step_size * np.sin(angle)
        ])
        
        new_pos = current_pos + step
        clamped_pos = self._clamp_to_bounds(new_pos)
        
        # Store for next iteration
        drone.last_search_pos = clamped_pos
        
        return clamped_pos
    
    def generate_perimeter_pattern(self, drone, simulation_step: int, margin=50) -> np.ndarray:
        """Generate perimeter search pattern around the edges"""
        # Calculate perimeter length
        perimeter = 2 * (self.width + self.height) - 8 * margin
        
        # Current position along perimeter
        progress = (simulation_step * 2 + drone.drone_id * 50) % perimeter
        
        # Determine which side of the perimeter we're on
        if progress < (self.width - 2 * margin):
            # Top edge
            return np.array([margin + progress, margin])
        elif progress < (self.width - 2 * margin) + (self.height - 2 * margin):
            # Right edge
            return np.array([self.width - margin, margin + (progress - (self.width - 2 * margin))])
        elif progress < 2 * (self.width - 2 * margin) + (self.height - 2 * margin):
            # Bottom edge
            return np.array([self.width - margin - (progress - (self.width - 2 * margin) - (self.height - 2 * margin)), self.height - margin])
        else:
            # Left edge
            remaining = progress - 2 * (self.width - 2 * margin) - (self.height - 2 * margin)
            return np.array([margin, self.height - margin - remaining])
    
    def generate_formation_pattern(self, drone, leader_pos: np.ndarray, formation_type="v_formation") -> np.ndarray:
        """Generate formation flying patterns"""
        if formation_type == "v_formation":
            return self._generate_v_formation(drone, leader_pos)
        elif formation_type == "line_formation":
            return self._generate_line_formation(drone, leader_pos)
        elif formation_type == "diamond_formation":
            return self._generate_diamond_formation(drone, leader_pos)
        else:
            return leader_pos  # Default to leader position
    
    def _generate_v_formation(self, drone, leader_pos: np.ndarray, spacing=30) -> np.ndarray:
        """Generate V-formation positions"""
        # Determine side based on drone ID
        side = 1 if drone.drone_id % 2 == 0 else -1
        position_in_formation = (drone.drone_id + 1) // 2
        
        offset = np.array([
            -position_in_formation * spacing,  # Behind leader
            side * position_in_formation * spacing  # To the side
        ])
        
        return leader_pos + offset
    
    def _generate_line_formation(self, drone, leader_pos: np.ndarray, spacing=25) -> np.ndarray:
        """Generate line formation positions"""
        offset = np.array([0, (drone.drone_id + 1) * spacing - len(getattr(drone, 'formation_drones', [1])) * spacing / 2])
        return leader_pos + offset
    
    def _generate_diamond_formation(self, drone, leader_pos: np.ndarray, spacing=35) -> np.ndarray:
        """Generate diamond formation positions"""
        positions = [
            np.array([0, 0]),           # Leader (center)
            np.array([-spacing, 0]),    # Left
            np.array([spacing, 0]),     # Right
            np.array([0, spacing]),     # Back
            np.array([-spacing/2, spacing/2]),  # Back-left
            np.array([spacing/2, spacing/2])    # Back-right
        ]
        
        if drone.drone_id < len(positions):
            return leader_pos + positions[drone.drone_id]
        else:
            # Fall back to line formation for additional drones
            return self._generate_line_formation(drone, leader_pos)
    
    def _clamp_to_bounds(self, position: np.ndarray, margin=30) -> np.ndarray:
        """Clamp position to screen bounds with margin"""
        clamped = position.copy()
        clamped[0] = max(margin, min(clamped[0], self.width - margin))
        clamped[1] = max(margin, min(clamped[1], self.height - margin))
        return clamped
    
    def get_pattern_info(self, pattern_type: SearchPattern, drone, simulation_step: int) -> Dict:
        """Get information about the current pattern state"""
        waypoint = self.generate_search_pattern(pattern_type, drone, simulation_step)
        
        return {
            'pattern_type': pattern_type.value,
            'current_waypoint': tuple(waypoint),
            'drone_id': drone.drone_id,
            'simulation_step': simulation_step,
            'distance_to_waypoint': np.linalg.norm(waypoint - drone.position) if hasattr(drone, 'position') else 0
        }