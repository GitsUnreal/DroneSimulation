from SimMode.ModeHandler import ModeHandler
from DroneSystem.Core.Drone import DroneMovementMode, DroneMovementConfig
from DroneSystem.Combat.Weapons.MissileSystem import MissileType, MissileConfigPresets

"""
Search and Rescue mode rules:
1. Drones should use stealth movement.
2. Drones should have a maximum of 8 missiles.
3. Drones should prefer homing missiles.
4. Drones should be hiding targets.
5. Drones should not show targets unless spotted by radar.
6. Drones should automatically use radar to detect targets.
7. Drones should automatically return to base when low on fuel.
8. Drones should not engage a target unless it has spotted the target.
"""

class SearchAndRescueRunModeHandler(ModeHandler):
    def __init__(self):
        super().__init__("search_and_rescue")
    
    def configure_drones(self, drones):
        movement_config = DroneMovementMode.STEALTH.value
        
        for drone in drones:
            drone.apply_movement_config(movement_config)
            drone.max_missiles = 8
            drone.preferred_missile_type = MissileType.HOMING
            drone.missile_config = MissileConfigPresets.HOMING.value

    def configure_drone(self, drone):
        """Configure individual drone for search and rescue mode"""
        movement_config = DroneMovementMode.STEALTH.value
        drone.apply_movement_config(movement_config)
        drone.max_missiles = 8
        drone.preferred_missile_type = MissileType.HOMING
        drone.missile_config = MissileConfigPresets.HOMING.value

    def configure_target(self, target):
        if hasattr(target, '__iter__') and not isinstance(target, str):
            for t in target:
                t.hidden = True
        else:
            target.hidden = True

    def get_movement_parameters(self):
        """Return movement parameters for search and rescue mode"""
        return DroneMovementMode.STEALTH.value.__dict__

    def get_missile_parameters(self):
        """Return missile parameters for search and rescue mode"""
        return MissileConfigPresets.HOMING.value.__dict__

    def should_show_target(self):
        return False  # Only show when spotted by radar