import numpy as np
from Utils.DroneUtils import DroneUtils

class DroneStateManager:
    """Manages drone states and lifecycle"""
    
    @staticmethod
    def get_drone_status_info(drone):
        """Get comprehensive status information for a drone"""
        active_missiles = len([m for m in getattr(drone, 'missiles', []) if m.get('active', False)])
        
        if not drone.alive:
            status = "Destroyed"
            color = "red"
        elif hasattr(drone, 'has_landed') and drone.has_landed:
            status = "Landed"
            color = "blue"
        elif hasattr(drone, 'returning_to_base') and drone.returning_to_base:
            status = "Returning"
            color = "orange"
        else:
            status = "Active"
            color = "green"
            
        return {
            'status': status,
            'color': color,
            'missiles_fired': drone.missiles_fired,
            'max_missiles': drone.max_missiles,
            'active_missiles': active_missiles,
            'text': f"Drone {drone.drone_id}: Missile Type: {drone.preferred_missile_type}, Missile Number: {drone.missiles_fired}/{drone.max_missiles} fired, {active_missiles}, active - {status}"
        }
    
    @staticmethod
    def reset_drones_to_safe_positions(drones, obstacles, base_center):
        """Reset all drones to safe positions around base"""
        spawn_radius = 20
        
        for i, drone in enumerate(drones):
            angle = (2 * np.pi * i) / len(drones)
            spawn_x = base_center[0] + spawn_radius * np.cos(angle)
            spawn_y = base_center[1] + spawn_radius * np.sin(angle)
            spawn_position = (spawn_x, spawn_y)
            
            # Find valid position with fallback logic
            valid_position = DroneStateManager._find_valid_spawn_position(
                spawn_position, obstacles, angle, base_center
            )
            
            DroneUtils.reset_drone_to_position(drone, valid_position)
    
    @staticmethod
    def _find_valid_spawn_position(initial_pos, obstacles, angle, base_center):
        """Find a valid spawn position with fallback logic"""
        from Utils.PositionUtils import PositionUtils
        
        # Try initial position
        if PositionUtils.is_position_valid(initial_pos, obstacles, width=20, height=20, margin=30):
            return initial_pos
        
        # Try different angles around base
        for attempt in range(36):
            test_angle = angle + (attempt * np.pi / 18)
            for radius in range(20, 100, 10):
                spawn_x = base_center[0] + radius * np.cos(test_angle)
                spawn_y = base_center[1] + radius * np.sin(test_angle)
                test_pos = (spawn_x, spawn_y)
                
                if PositionUtils.is_position_valid(test_pos, obstacles, width=20, height=20, margin=10):
                    return test_pos
        
        # Fallback to original position if nothing works
        return initial_pos