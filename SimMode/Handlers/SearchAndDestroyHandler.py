from SimMode.ModeHandler import ModeHandler
from DroneSystem.Drone import DroneMovementMode, DroneMovementConfig
from DroneSystem.MissileSystem import MissileType, MissileConfigPresets

"""
Search and Destroy mode rules:
1. Drones should use stealth movement.
2. Drones should have a maximum of 8 missiles.
3. Drones should prefer explosive missiles.
4. Drones should be hiding targets.
5. Drones should not show targets unless spotted by radar.
6. Drones should autommatically use radar to detect targets.
7. Drones should automaticcaly return to base when low on fuel.
8. Drones should not engage a target unless it has spotted the target.
"""

class SearchAndDestroyModeHandler(ModeHandler):
    def __init__(self):
        super().__init__("search_and_destroy")
    
    def configure_drones(self, drones):
        # Use fast assault movement for search and destroy
        movement_config = DroneMovementMode.FAST_ASSAULT.value
        
        for drone in drones:
            drone.apply_movement_config(movement_config)
            drone.max_missiles = 6
            drone.preferred_missile_type = MissileType.HOMING
            drone.missile_config = MissileConfigPresets.HOMING.value

    def configure_target(self, target):
        # Handle both single target and multiple targets - KEEP HIDDEN UNTIL SPOTTED
        if hasattr(target, '__iter__') and not isinstance(target, str):
            # Multiple targets
            for t in target:
                t.hidden = True
                t.spotted_by_radar = False  # Add spotted flag
        else:
            # Single target
            target.hidden = True
            target.spotted_by_radar = False  # Add spotted flag
    
    def get_movement_parameters(self):
        return DroneMovementMode.FAST_ASSAULT.value.__dict__
    
    def get_missile_parameters(self):
        return MissileConfigPresets.HOMING.value.__dict__
    
    def should_show_target(self):
        return False  # Never show target unless spotted by radar