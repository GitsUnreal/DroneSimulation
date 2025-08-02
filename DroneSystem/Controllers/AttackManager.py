import numpy as np
from DroneSystem.Combat.Weapons.MissileSystem import MissileType


class AttackManager:
    @staticmethod
    def handle_attack(drone, main_controller):
        """Handle missile attack logic for a drone."""
        if main_controller.distance_to_target(drone) < 100 and not drone.has_attacked:
            if drone.can_fire_missile():
                try:
                    target_pos = main_controller.get_target_position()
                    target_coords = (target_pos[0], target_pos[1])
                except Exception:
                    target_coords = (120.0, 660.0)
                success = main_controller.missile_manager.fire_missile(
                    drone,
                    target_coords,
                    MissileType.HOMING
                )
                if success and drone.missiles_fired >= drone.max_missiles:
                    drone.has_attacked = True
            else:
                drone.has_attacked = True
