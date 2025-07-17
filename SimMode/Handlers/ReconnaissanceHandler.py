from SimMode.ModeHandler import ModeHandler
from DroneSystem.Core.Drone import DroneMovementMode, DroneMovementConfig
from DroneSystem.Combat.Weapons.MissileSystem import MissileType, MissileConfigPresets


"""
Reconnaissance mode rules:
1. Drones should use stealth movement.
2. Drones should have a maximum of 2 missiles.
3. Drones should prefer homing missiles.
4. Drones should be hiding targets.
5. Drones should not show targets unless spotted by radar.
6. Drones should not engage targets unless they are spotted.
7. Drones should not use any weapons unless giving command to fire.
8. Drones should automatically use radar to detect targets.
9. Drones should automatically return to base when low on fuel.
"""

class ReconnaissanceModeHandler(ModeHandler):
    def __init__(self):
        super().__init__("reconnaissance")
    
    def configure_drones(self, drones):
        # Use stealth movement for reconnaissance
        movement_config = DroneMovementMode.STEALTH.value
        
        for drone in drones:
            drone.apply_movement_config(movement_config)
            drone.max_missiles = 2  # Light armament for stealth
            drone.preferred_missile_type = MissileType.HOMING
            drone.missile_config = MissileConfigPresets.HOMING.value

    def configure_drone(self, drone):
        """Configure individual drone for reconnaissance mode"""
        movement_config = DroneMovementMode.STEALTH.value
        drone.apply_movement_config(movement_config)
        drone.max_missiles = 2
        drone.preferred_missile_type = MissileType.HOMING
        drone.missile_config = MissileConfigPresets.HOMING.value

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
        """Return movement parameters for reconnaissance mode"""
        return DroneMovementMode.STEALTH.value.__dict__

    def get_missile_parameters(self):
        """Return missile parameters for reconnaissance mode"""
        return MissileConfigPresets.HOMING.value.__dict__

    def should_show_target(self):
        return False  # Only show when spotted by radar