from SimMode.ModeHandler import ModeHandler
from AI.Drone import DroneMovementMode, DroneMovementConfig
from AI.MissileSystem import MissileType, MissileConfigPresets

class BombingRunModeHandler(ModeHandler):
    def __init__(self):
        super().__init__("bombing_run")
    
    def configure_drones(self, drones):
        # Use standard movement for bombing runs
        movement_config = DroneMovementMode.STANDARD.value
        
        for drone in drones:
            drone.apply_movement_config(movement_config)
            drone.max_missiles = 8
            drone.preferred_missile_type = MissileType.EXPLOSIVE
            drone.missile_config = MissileConfigPresets.EXPLOSIVE.value

    def configure_target(self, target):
        target.hidden = False
    
    def get_movement_parameters(self):
        return DroneMovementMode.STANDARD.value.__dict__
    
    def get_missile_parameters(self):
        return MissileConfigPresets.EXPLOSIVE.value.__dict__
    
    def should_show_target(self):
        return True