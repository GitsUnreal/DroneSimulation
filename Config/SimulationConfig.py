class SimulationConfig:
    """Centralized configuration for the simulation"""
    
    # Window settings
    WINDOW_WIDTH = 1080
    WINDOW_HEIGHT = 720
    CONTROL_PANEL_HEIGHT = 35
    
    # Simulation settings
    TIMER_INTERVAL = 50  # 50ms = 20 FPS
    CELL_SIZE = 10
    
    # Drone settings
    DEFAULT_DRONES = 2
    DRONE_SIZE = 20
    SPAWN_RADIUS = 20
    SPAWN_MARGIN = 30
    
    # Base settings
    BASE_SIZE = 20
    BASE_POSITION = (50, 50)
    
    # UI Colors
    COLORS = {
        'start_button': 'lightgreen',
        'reset_button': 'lightcoral',
        'grid_button': 'lightblue',
        'path_button': 'lightyellow',
        'debug_button': 'lightgray',
        'stats_button': 'lightcyan',
        'perf_button': 'lightpink',
        'radar_button': 'lightsteelblue',
        'active_button': 'lightgreen'
    }