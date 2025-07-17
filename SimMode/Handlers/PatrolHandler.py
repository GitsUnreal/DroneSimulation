from SimMode.ModeHandler import ModeHandler
from DroneSystem.Core.Drone import DroneMovementMode, DroneMovementConfig
from DroneSystem.Combat.Weapons.MissileSystem import MissileType, MissileConfigPresets


"""
Patrol mode rules:
1. Drones should use Patrol movement.
2. Drones should have a maximum of 8 missiles.
3. Drones should prefer explosive missiles.
4. Drones should not hide targets.
"""

class PatrolModeHandler(ModeHandler):
    def __init__(self):
        super().__init__("patrol")
    
    def configure_drones(self, drones):
        movement_config = DroneMovementMode.PATROL.value
        
        for drone in drones:
            drone.apply_movement_config(movement_config)
            drone.max_missiles = 8
            drone.preferred_missile_type = MissileType.EXPLOSIVE
            drone.missile_config = MissileConfigPresets.EXPLOSIVE.value

    def configure_drone(self, drone):
        """Configure individual drone for patrol mode"""
        movement_config = DroneMovementMode.PATROL.value
        drone.apply_movement_config(movement_config)
        drone.max_missiles = 8
        drone.preferred_missile_type = MissileType.EXPLOSIVE
        drone.missile_config = MissileConfigPresets.EXPLOSIVE.value

    def configure_target(self, target):
        if hasattr(target, '__iter__') and not isinstance(target, str):
            for t in target:
                t.hidden = False
        else:
            target.hidden = False
    
    def get_movement_parameters(self):
        """Return movement parameters for patrol mode"""
        return DroneMovementMode.PATROL.value.__dict__
    
    def get_missile_parameters(self):
        """Return missile parameters for patrol mode"""
        return MissileConfigPresets.EXPLOSIVE.value.__dict__
    
    def should_show_target(self):
        return True