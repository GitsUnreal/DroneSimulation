from SimMode.ModeHandler import ModeHandler
from DroneSystem.Core.Drone import DroneMovementMode, DroneMovementConfig
from DroneSystem.Combat.Weapons.MissileSystem  import MissileType, MissileConfigPresets


"""
Bombing run rules:
1. Drones should use fast assault movement.
2. Drones should have a maximum of 8 missiles.
3. Drones should prefer explosive missiles.
4. Drones should not hide targets.
"""

class BombingRunModeHandler(ModeHandler):
    def __init__(self):
        super().__init__("bombing_run")
    
    def configure_drones(self, drones):
        # Use standard movement for bombing runs
        movement_config = DroneMovementMode.FAST_ASSAULT.value
        
        for drone in drones:
            drone.apply_movement_config(movement_config)
            drone.max_missiles = 8
            drone.preferred_missile_type = MissileType.EXPLOSIVE
            drone.missile_config = MissileConfigPresets.EXPLOSIVE.value

    def configure_target(self, target):
        # Handle both single target and multiple targets
        if hasattr(target, '__iter__') and not isinstance(target, str):
            # Multiple targets
            for t in target:
                t.hidden = False
        else:
            # Single target
            target.hidden = False
    
    def get_movement_parameters(self):
        return DroneMovementMode.FAST_ASSAULT.value.__dict__
    
    def get_missile_parameters(self):
        return MissileConfigPresets.EXPLOSIVE.value.__dict__
    
    def should_show_target(self):
        return True