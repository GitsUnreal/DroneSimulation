"""Drone configuration settings"""

class DroneConfig:
    """Configuration for drone behavior and properties"""
    
    # Basic drone settings
    DEFAULT_DRONES = 2
    DRONE_SIZE = 20
    SPAWN_RADIUS = 20
    SPAWN_MARGIN = 30
    MAX_MISSILES = 2
    
    # Movement parameters
    DEFAULT_VELOCITY = 2.0
    DEFAULT_TURN_RATE = 0.1
    MAX_VELOCITY = 5.0
    MIN_VELOCITY = 0.5
    
    # Physics
    ACCELERATION = 0.1
    FRICTION = 0.95
    
    # Combat
    MISSILE_SPEED = 4.0
    MISSILE_RANGE = 200
    RELOAD_TIME = 3.0
    
    # AI behavior
    SEPARATION_RADIUS = 30
    ALIGNMENT_RADIUS = 50
    COHESION_RADIUS = 80
    
    @classmethod
    def get_default_config(cls):
        """Get default drone configuration as dictionary"""
        return {
            'velocity': cls.DEFAULT_VELOCITY,
            'turn_rate': cls.DEFAULT_TURN_RATE,
            'max_velocity': cls.MAX_VELOCITY,
            'size': cls.DRONE_SIZE
        }