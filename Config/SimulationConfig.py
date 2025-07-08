"""Simulation configuration settings"""

class SimulationConfig:
    """Configuration for the simulation environment"""
    
    # Window settings
    WINDOW_WIDTH = 1080
    WINDOW_HEIGHT = 720
    CONTROL_PANEL_HEIGHT = 35
    
    # Simulation settings
    TIMER_INTERVAL = 50  # 50ms = 20 FPS
    CELL_SIZE = 10
    MAX_FPS = 60
    
    # Base settings
    BASE_SIZE = 20
    BASE_POSITION = (50, 50)
    SPAWN_RADIUS = 20
    
    # Grid settings
    GRID_ENABLED = True
    GRID_SIZE = 50
    GRID_COLOR = (200, 200, 200)
    
    # Simulation bounds
    MIN_X = 0
    MIN_Y = 0
    MAX_X = WINDOW_WIDTH
    MAX_Y = WINDOW_HEIGHT
    
    @classmethod
    def get_window_size(cls):
        """Get window dimensions as tuple"""
        return (cls.WINDOW_WIDTH, cls.WINDOW_HEIGHT)
    
    @classmethod
    def get_simulation_bounds(cls):
        """Get simulation bounds as rectangle"""
        return (cls.MIN_X, cls.MIN_Y, cls.MAX_X, cls.MAX_Y)
    
    # UI Colors
    COLORS = {
        'start_button': 'lightgreen',
        'reset_button': 'lightcoral', 
        'grid_button': 'lightblue',
        'path_button': 'lightblue',
        'debug_button': 'lightblue',
        'stats_button': 'lightblue',
        'perf_button': 'lightblue',
        'radar_button': 'lightblue',
        'active_button': 'orange'
    }
    DEFAULT_DRONES = 3
    DRONE_SIZE = 15
    TARGET_SIZE = 30
    BASE_X = 50
    BASE_Y = 50
    BASE_WIDTH = 100
    BASE_HEIGHT = 50
