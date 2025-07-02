from SimMode.ModeHandler import ModeHandler
from AI.Drone import DroneMovementMode, DroneMovementConfig
from AI.MissileSystem import MissileType, MissileConfigPresets

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
        target.hidden = True
    
    def get_movement_parameters(self):
        return DroneMovementMode.FAST_ASSAULT.value.__dict__
    
    def get_missile_parameters(self):
        return MissileConfigPresets.HOMING.value.__dict__
    
    def should_show_target(self):
        return False