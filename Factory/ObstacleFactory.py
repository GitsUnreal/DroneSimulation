import random
import numpy as np
from PyQt5.QtCore import QRect
from GUI.Objects.Obstacle import Obstacle
from Utils.PositionUtils import PositionUtils
from Config.SimulationConfig import SimulationConfig

class ObstacleFactory:
    """Factory for creating different types of obstacles"""
    
    @staticmethod
    def create_obstacle(x, y, size=40, obstacle_type="standard"):
        """Create a single obstacle at specified position"""
        return Obstacle(x, y, size, size)
    
    @staticmethod
    def create_random_obstacle(width=SimulationConfig.WINDOW_WIDTH, height=SimulationConfig.WINDOW_HEIGHT, 
                              existing_obstacles=None, margin=50):
        """Create a randomly positioned obstacle that doesn't overlap with existing ones"""
        existing_obstacles = existing_obstacles or []
        
        # Try to find a valid position
        for _ in range(100):  # Max attempts
            size = random.randint(30, 80)
            x = random.randint(margin, width - size - margin)
            y = random.randint(margin, height - size - margin)
            
            # Check if this position conflicts with existing obstacles
            new_obstacle = Obstacle(x, y, size, size)
            if not ObstacleFactory._overlaps_with_existing(new_obstacle, existing_obstacles):
                return new_obstacle
        
        # Fallback: create at a safe position
        return Obstacle(margin, margin, 40, 40)
    
    @staticmethod
    def create_obstacle_field(count=5, width=SimulationConfig.WINDOW_WIDTH, 
                             height=SimulationConfig.WINDOW_HEIGHT, margin=100):
        """Create a field of random obstacles"""
        obstacles = []
        
        for _ in range(count):
            obstacle = ObstacleFactory.create_random_obstacle(
                width, height, obstacles, margin
            )
            obstacles.append(obstacle)
        
        return obstacles
    
    @staticmethod
    def create_obstacle_maze(density=0.3, cell_size=60, 
                           width=SimulationConfig.WINDOW_WIDTH, 
                           height=SimulationConfig.WINDOW_HEIGHT):
        """Create a maze-like obstacle pattern"""
        obstacles = []
        
        cols = width // cell_size
        rows = height // cell_size
        
        for row in range(rows):
            for col in range(cols):
                if random.random() < density:
                    x = col * cell_size
                    y = row * cell_size
                    # Vary the size slightly for more natural look
                    size = cell_size + random.randint(-10, 10)
                    obstacles.append(Obstacle(x, y, size, size))
        
        return obstacles
    
    @staticmethod
    def create_obstacle_corridor(corridor_width=100, num_gaps=3,
                               width=SimulationConfig.WINDOW_WIDTH,
                               height=SimulationConfig.WINDOW_HEIGHT):
        """Create a corridor with obstacles on both sides and gaps for passage"""
        obstacles = []
        
        # Create obstacles on top and bottom, leaving gaps
        gap_size = width // (num_gaps + 1)
        
        for i in range(num_gaps + 1):
            if i < num_gaps:  # Don't create obstacle after last gap
                # Top obstacles
                gap_start = i * gap_size + gap_size // 2
                gap_end = gap_start + corridor_width
                
                # Left side of gap
                if gap_start > 0:
                    obstacles.append(Obstacle(0, 0, gap_start, height // 3))
                
                # Right side of gap
                if gap_end < width:
                    obstacles.append(Obstacle(gap_end, 0, width - gap_end, height // 3))
                
                # Bottom obstacles (mirrored)
                if gap_start > 0:
                    obstacles.append(Obstacle(0, 2 * height // 3, gap_start, height // 3))
                
                if gap_end < width:
                    obstacles.append(Obstacle(gap_end, 2 * height // 3, width - gap_end, height // 3))
        
        return obstacles
    
    @staticmethod
    def create_strategic_obstacles(drones, target, base, num_obstacles=6):
        """Create obstacles that make the scenario more challenging"""
        obstacles = []
        
        # Create some obstacles between drones and target
        if target and drones:
            avg_drone_pos = np.mean([drone.position for drone in drones], axis=0)
            target_pos = np.array([target.position[0], target.position[1]])
            
            # Create obstacles along the path
            direction = target_pos - avg_drone_pos
            distance = np.linalg.norm(direction)
            
            if distance > 0:
                direction = direction / distance
                
                for i in range(1, num_obstacles + 1):
                    # Place obstacles at intervals along the path
                    offset_distance = (distance / (num_obstacles + 1)) * i
                    pos = avg_drone_pos + direction * offset_distance
                    
                    # Add some randomness to position
                    pos[0] += random.randint(-50, 50)
                    pos[1] += random.randint(-50, 50)
                    
                    # Ensure obstacle is within bounds
                    pos[0] = max(50, min(SimulationConfig.WINDOW_WIDTH - 50, pos[0]))
                    pos[1] = max(50, min(SimulationConfig.WINDOW_HEIGHT - 50, pos[1]))
                    
                    size = random.randint(40, 70)
                    obstacles.append(Obstacle(int(pos[0]), int(pos[1]), size, size))
        
        return obstacles
    
    @staticmethod
    def create_escort_obstacles(convoy_path, num_obstacles=8):
        """Create obstacles for escort missions that threaten the convoy route"""
        obstacles = []
        
        if not convoy_path or len(convoy_path) < 2:
            return ObstacleFactory.create_obstacle_field(num_obstacles)
        
        # Create obstacles near the convoy path to create threat scenarios
        for i in range(num_obstacles):
            # Pick a random point along the convoy path
            path_index = random.randint(0, len(convoy_path) - 1)
            path_point = convoy_path[path_index]
            
            # Create obstacles near but not on the path
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(80, 150)  # Close enough to be threatening
            
            x = path_point[0] + distance * np.cos(angle)
            y = path_point[1] + distance * np.sin(angle)
            
            # Ensure obstacle is within bounds
            x = max(50, min(SimulationConfig.WINDOW_WIDTH - 50, x))
            y = max(50, min(SimulationConfig.WINDOW_HEIGHT - 50, y))
            
            size = random.randint(30, 60)
            obstacles.append(Obstacle(int(x), int(y), size, size))
        
        return obstacles
    
    @staticmethod
    def _overlaps_with_existing(new_obstacle, existing_obstacles, buffer=20):
        """Check if a new obstacle overlaps with existing ones"""
        new_rect = QRect(
            new_obstacle.x() - buffer, 
            new_obstacle.y() - buffer,
            new_obstacle.width() + 2 * buffer, 
            new_obstacle.height() + 2 * buffer
        )
        
        for obstacle in existing_obstacles:
            existing_rect = QRect(
                obstacle.x(), obstacle.y(), 
                obstacle.width(), obstacle.height()
            )
            if new_rect.intersects(existing_rect):
                return True
        
        return False
    
    @staticmethod
    def create_obstacle_by_type(obstacle_type, **kwargs):
        """Create obstacles based on mission type or specific requirements"""
        
        obstacle_types = {
            'random_field': lambda: ObstacleFactory.create_obstacle_field(**kwargs),
            'maze': lambda: ObstacleFactory.create_obstacle_maze(**kwargs),
            'corridor': lambda: ObstacleFactory.create_obstacle_corridor(**kwargs),
            'strategic': lambda: ObstacleFactory.create_strategic_obstacles(**kwargs),
            'escort': lambda: ObstacleFactory.create_escort_obstacles(**kwargs),
            'single': lambda: [ObstacleFactory.create_obstacle(**kwargs)],
            'empty': lambda: []
        }
        
        creator = obstacle_types.get(obstacle_type, obstacle_types['random_field'])
        return creator()

    @staticmethod
    def get_obstacle_info(obstacle):
        """Get information about an obstacle for debugging/display"""
        return {
            'position': (obstacle.x(), obstacle.y()),
            'size': (obstacle.width(), obstacle.height()),
            'area': obstacle.width() * obstacle.height(),
            'center': (obstacle.x() + obstacle.width()//2, obstacle.y() + obstacle.height()//2)
        }