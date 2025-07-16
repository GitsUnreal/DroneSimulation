from ..States.DroneStateManager import DroneStateManager

class StateController:
    def __init__(self, drones, base, alert_system):
        self.drones = drones
        self.base = base
        self.alert_system = alert_system
        self.state_manager = DroneStateManager()
    
    def should_skip_drone(self, drone):
        """Check if drone should be skipped in updates"""
        return drone.is_destroyed() or (hasattr(drone, 'has_landed') and drone.has_landed)
    
    def update_drone_state(self, drone, base):
        """Update individual drone state"""
        # Check if drone should return to base
        if drone.has_attacked and not hasattr(drone, 'returning_to_base'):
            drone.returning_to_base = True
        
        # Check if drone has reached base
        if hasattr(drone, 'returning_to_base') and drone.returning_to_base:
            base_distance = self._distance_to_base(drone, base)
            if base_distance < 30:
                drone.land_at_base()
                drone.returning_to_base = False
    
    def process_alerts(self):
        """Process all pending alerts"""
        for drone in self.drones:
            if not drone.alive and not hasattr(drone, '_destruction_alerted'):
                self.alert_system.show_drone_destroyed_alert(drone.drone_id)
                drone._destruction_alerted = True
    
    def is_mission_complete(self):
        """Check if mission is complete"""
        return all(hasattr(drone, 'has_landed') and drone.has_landed for drone in self.drones)
    
    def _distance_to_base(self, drone, base):
        """Calculate distance from drone to base"""
        import numpy as np
        return np.linalg.norm(np.array([base.x(), base.y()]) - drone.position)