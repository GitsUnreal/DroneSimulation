from SimMode.ModeHandler import ModeHandler
from DroneSystem.Core.Drone import DroneMovementMode, DroneMovementConfig
from DroneSystem.Combat.Weapons.MissileSystem  import MissileType, MissileConfigPresets


"""
Normal mode rules:
1. Drones should use standard movement.
2. Drones should have a maximum of 8 missiles.
3. Drones should prefer explosive missiles.
4. Drones should not hide targets.
"""

class NormalModeHandler(ModeHandler):
    def __init__(self):
        super().__init__("normal_mode")
    
    def configure_drones(self, drones):
        # Use standard movement for bombing runs
        movement_config = DroneMovementMode.STANDARD.value
        
        for drone in drones:
            drone.apply_movement_config(movement_config)
            drone.max_missiles = 8
            drone.preferred_missile_type = MissileType.HOMING
            drone.missile_config = MissileConfigPresets.HOMING.value

    def configure_target(self, target):
        """Configure target for normal mode"""
        if target is None:
            return  # Skip configuration for None target
            
        target.hidden = False
        target.is_moving_target = False
        if hasattr(target, 'speed'):
            target.speed = 0
    
    def get_movement_parameters(self):
        return DroneMovementMode.STANDARD.value.__dict__
    
    def get_missile_parameters(self):
        return MissileConfigPresets.HOMING.value.__dict__
    
    def should_show_target(self):
        return True