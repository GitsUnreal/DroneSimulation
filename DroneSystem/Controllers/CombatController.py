from ..Combat.Weapons.MissileManager import MissileManager, MissileType
from ..Combat.Targeting.TargetPredictor import TargetPredictor

class CombatController:
    def __init__(self, target, alert_system):
        self.target = target
        self.alert_system = alert_system
        self.missile_manager = MissileManager(None, {})  # Will be properly initialized
        self.target_predictor = TargetPredictor()
        
        if target:
            self.missile_manager.set_target(target)
    
    def update_target(self, new_target):
        """Update target reference"""
        self.target = new_target
        self.missile_manager.set_target(new_target)
    
    def update_missiles(self, drones, obstacles):
        """Update all missiles and check for target hits"""
        self.missile_manager.update_missiles(0.05, drones, obstacles)
        
        # Check for target hits
        for missile in self.missile_manager.get_active_missiles():
            if (hasattr(missile, 'hit_target') and missile.hit_target and 
                missile.state.value == "exploding"):
                if not self.target.is_destroyed():
                    self.target.destroy()
                    return True
        return False
    
    def handle_drone_combat(self, drone, target):
        """Handle combat logic for a single drone"""
        if not self._should_attack(drone, target):
            return
        
        if not drone.can_fire_missile():
            drone.has_attacked = True
            return
        
        # Determine target position (predicted for moving targets)
        target_pos = self._get_target_position(target)
        
        # Fire missile
        missile_type = getattr(drone, 'preferred_missile_type', MissileType.STANDARD)
        success = self.missile_manager.fire_missile(drone, target_pos, missile_type)
        
        if success and drone.missiles_fired >= drone.max_missiles:
            drone.has_attacked = True
    
    def _should_attack(self, drone, target):
        """Determine if drone should attack"""
        return (self._distance_to_target(drone, target) < 100 and 
                not drone.has_attacked)
    
    def _get_target_position(self, target):
        """Get optimal target position (with prediction for moving targets)"""
        if hasattr(target, 'is_moving_target') and target.is_moving_target:
            return self.target_predictor.predict_position(target, 1.0)
        return (target.x(), target.y())
    
    def _distance_to_target(self, drone, target):
        """Calculate distance from drone to target"""
        import numpy as np
        return np.linalg.norm(
            np.array([target.position[0], target.position[1]]) - drone.position
        )