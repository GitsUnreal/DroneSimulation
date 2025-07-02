from SimMode.ModeHandler import ModeHandler
from AI.Drone import DroneMovementMode, DroneMovementConfig
from AI.MissileSystem import MissileType, MissileConfigPresets

class ReconnaissanceModeHandler(ModeHandler):
    def __init__(self):
        super().__init__("reconnaissance")
    
    def configure_drones(self, drones):
        # Use stealth movement for reconnaissance
        movement_config = DroneMovementMode.STEALTH.value
        
        for drone in drones:
            drone.apply_movement_config(movement_config)
            drone.max_missiles = 2  # Light armament for stealth
            drone.preferred_missile_type = MissileType.STANDARD
            drone.missile_config = MissileConfigPresets.STANDARD.value

    def configure_target(self, target):
        # Handle both single target and multiple targets
        if hasattr(target, '__iter__') and not isinstance(target, str):
            # Multiple targets
            for t in target:
                t.hidden = True
        else:
            # Single target
            target.hidden = True
    
    def get_movement_parameters(self):
        return DroneMovementMode.STEALTH.value.__dict__
    
    def get_missile_parameters(self):
        return MissileConfigPresets.STANDARD.value.__dict__
    
    def should_show_target(self):
        return False