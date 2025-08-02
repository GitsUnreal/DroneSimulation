from SimMode.ModeHandler import ModeHandler
from DroneSystem.Core.Drone import DroneMovementMode, DroneMovementConfig
from DroneSystem.Combat.Weapons.MissileSystem import MissileType, MissileConfigPresets

"""
Escort mode rules:
1. Drones should use standard movement for formation flying.
2. Drones should have a maximum of 4 missiles (light armament for protection).
3. Drones should prefer standard missiles for quick response.
4. Drones should not hide targets - they need to see threats.
5. Drones should maintain formation around the VIP/convoy.
6. Drones should prioritize defensive positioning.
7. Drones should only engage threats that come too close.
8. Drones should automatically use radar to detect incoming threats.
"""


from typing import List, Any, Dict, Tuple

class EscortModeHandler(ModeHandler):
    """
    Handler for Escort simulation mode. Drones protect VIP/convoy, maintain formation,
    and prioritize defensive actions.
    """
    def __init__(self) -> None:
        super().__init__("escort")

    def configure_drones(self, drones: List[Any]) -> None:
        """
        Configure all drones for escort mode.
        Args:
            drones (List[Any]): List of drone objects.
        """
        movement_config = DroneMovementMode.STANDARD.value
        for drone in drones:
            self.configure_drone(drone)

    def configure_drone(self, drone: Any) -> None:
        """
        Configure a single drone for escort mode.
        Args:
            drone (Any): Drone object.
        """
        movement_config = DroneMovementMode.STANDARD.value
        drone.apply_movement_config(movement_config)
        drone.max_missiles = 4
        drone.preferred_missile_type = MissileType.STANDARD
        drone.missile_config = MissileConfigPresets.STANDARD.value

    def configure_target(self, target: Any) -> None:
        """
        Configure the target(s) for escort mode (VIP/convoy).
        Args:
            target (Any): Target object or list of targets.
        """
        if hasattr(target, '__iter__') and not isinstance(target, str):
            for t in target:
                self._set_vip_properties(t)
        else:
            self._set_vip_properties(target)

    @staticmethod
    def _set_vip_properties(target: Any) -> None:
        target.hidden = False
        target.is_vip = True
        target.needs_escort = True

    def get_movement_parameters(self) -> Dict:
        """Return movement parameters for escort mode."""
        return DroneMovementMode.STANDARD.value.__dict__

    def get_missile_parameters(self) -> Dict:
        """Return missile parameters for escort mode."""
        return MissileConfigPresets.STANDARD.value.__dict__

    def should_show_target(self) -> bool:
        """Always show the VIP/escort target."""
        return True

    def get_formation_type(self) -> str:
        """Get the preferred formation for escort missions."""
        return "protective_circle"

    def get_threat_priority(self, threats: List[Any], vip_position: Tuple[float, float]) -> List[Tuple[Any, float]]:
        """
        Prioritize threats based on distance to VIP.
        Args:
            threats (List[Any]): List of threat objects with position attribute.
            vip_position (Tuple[float, float]): Position of VIP.
        Returns:
            List[Tuple[Any, float]]: List of (threat, priority) sorted by priority descending.
        """
        threat_priorities = []
        for threat in threats:
            distance_to_vip = ((threat.position[0] - vip_position[0]) ** 2 +
                              (threat.position[1] - vip_position[1]) ** 2) ** 0.5
            priority = 1000 - distance_to_vip
            threat_priorities.append((threat, priority))
        return sorted(threat_priorities, key=lambda x: x[1], reverse=True)