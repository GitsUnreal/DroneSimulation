"""
UI event definitions and types
"""
from enum import Enum

class UIEventType(Enum):
    SIMULATION_TOGGLE = "simulation_toggle"
    SIMULATION_RESET = "simulation_reset"
    GRID_TOGGLE = "grid_toggle"
    PATHS_TOGGLE = "paths_toggle"
    DEBUG_TOGGLE = "debug_toggle"
    RADAR_TOGGLE = "radar_toggle"
    MODE_CHANGE = "mode_change"
    SPEED_CHANGE = "speed_change"
    TARGET_DESTROYED = "target_destroyed"
    DRONE_DESTROYED = "drone_destroyed"

class UIEvent:
    def __init__(self, event_type, data=None):
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = None
    
    def __str__(self):
        return f"UIEvent({self.event_type}, {self.data})"
