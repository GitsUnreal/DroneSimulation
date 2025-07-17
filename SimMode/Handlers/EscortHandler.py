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

class EscortModeHandler(ModeHandler):
    def __init__(self):
        super().__init__("escort")
    
    def configure_drones(self, drones):
        # Use standard movement for formation escort
        movement_config = DroneMovementMode.STANDARD.value
        
        for drone in drones:
            drone.apply_movement_config(movement_config)
            drone.max_missiles = 4  # Light armament for quick response
            drone.preferred_missile_type = MissileType.STANDARD
            drone.missile_config = MissileConfigPresets.STANDARD.value
            
            # Set escort-specific properties
            drone.escort_range = 100  # How close to stay to VIP
            drone.threat_engagement_range = 150  # Only engage threats within this range
            drone.formation_priority = True  # Prioritize formation over individual targets

    def configure_target(self, target):
        # In escort missions, the "target" is actually the VIP/convoy to protect
        # Handle both single target and multiple targets
        if hasattr(target, '__iter__') and not isinstance(target, str):
            # Multiple targets (convoy)
            for t in target:
                t.hidden = False  # Always visible - this is what we're protecting
                t.is_vip = True  # Mark as VIP
                t.needs_escort = True
        else:
            # Single target (VIP)
            target.hidden = False  # Always visible
            target.is_vip = True  # Mark as VIP
            target.needs_escort = True
    
    def get_movement_parameters(self):
        return DroneMovementMode.STANDARD.value.__dict__
    
    def get_missile_parameters(self):
        return MissileConfigPresets.STANDARD.value.__dict__
    
    def should_show_target(self):
        return True  # Always show the VIP/convoy being escorted
    
    def get_formation_type(self):
        """Get the preferred formation for escort missions"""
        return "protective_circle"  # Drones form a circle around the VIP
    
    def get_threat_priority(self, threats, vip_position):
        """Prioritize threats based on distance to VIP"""
        threat_priorities = []
        for threat in threats:
            distance_to_vip = ((threat.position[0] - vip_position[0])**2 + 
                              (threat.position[1] - vip_position[1])**2)**0.5
            priority = 1000 - distance_to_vip  # Closer = higher priority
            threat_priorities.append((threat, priority))
        
        return sorted(threat_priorities, key=lambda x: x[1], reverse=True)