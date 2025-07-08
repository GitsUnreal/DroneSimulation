"""Drone state management system"""
from enum import Enum

class DroneState(Enum):
    IDLE = "idle"
    PATROL = "patrol"
    ATTACK = "attack"
    RETURN = "return"
    LANDED = "landed"

class DroneStateManager:
    """Manages drone states and transitions"""
    
    def __init__(self, drone_id):
        self.drone_id = drone_id
        self.current_state = DroneState.IDLE
        self.previous_state = DroneState.IDLE
        self.state_data = {}
        
    def set_state(self, new_state, data=None):
        """Set new drone state"""
        self.previous_state = self.current_state
        self.current_state = new_state
        if data:
            self.state_data.update(data)
            
    def get_state(self):
        """Get current state"""
        return self.current_state
        
    def is_state(self, state):
        """Check if drone is in specific state"""
        return self.current_state == state
        
    def update(self, dt):
        """Update state manager"""
        pass
    
    @staticmethod
    def get_drone_status_info(drone):
        """Get formatted status information for a drone"""
        if not drone.alive:
            return {
                'text': f"Drone {drone.drone_id}: DESTROYED",
                'color': '#FF0000'
            }
        elif hasattr(drone, 'has_landed') and drone.has_landed:
            return {
                'text': f"Drone {drone.drone_id}: LANDED",
                'color': '#888888'
            }
        elif drone.missiles_fired >= drone.max_missiles:
            return {
                'text': f"Drone {drone.drone_id}: No missiles ({drone.missiles_fired}/{drone.max_missiles})",
                'color': '#FF8800'
            }
        else:
            return {
                'text': f"Drone {drone.drone_id}: {drone.missiles_fired}/{drone.max_missiles} missiles",
                'color': '#00AA00'
            }
