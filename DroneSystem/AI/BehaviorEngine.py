class BehaviorEngine:
    def __init__(self, sim_modes):
        self.sim_modes = sim_modes
    
    def get_drone_behavior(self, drone, target, simulation_step):
        """Determine what behavior a drone should exhibit"""
        # Check if drone is returning to base
        if hasattr(drone, 'returning_to_base') and drone.returning_to_base:
            return {
                'type': 'return',
                'target_position': (self.sim_modes.base.x(), self.sim_modes.base.y()),
                'use_pathfinding': True,
                'movement_params': self._get_return_movement_params()
            }
        
        # Check if target is hidden and needs searching
        if (hasattr(target, 'hidden') and target.hidden and 
            not getattr(target, 'spotted_by_radar', False)):
            return {
                'type': 'search',
                'pattern': self._get_search_pattern(),
                'movement_params': self._get_search_movement_params()
            }
        
        # Default to attack behavior
        return {
            'type': 'attack',
            'target': target,
            'target_position': (target.position[0], target.position[1]),
            'movement_params': self._get_attack_movement_params()
        }
    
    def _get_search_pattern(self):
        """Get search pattern based on current mode"""
        if self.sim_modes:
            handler = self.sim_modes.get_current_handler()
            return getattr(handler, 'search_pattern', 'spiral')
        return 'spiral'
    
    def _get_search_movement_params(self):
        """Get movement parameters for search behavior"""
        if self.sim_modes:
            return self.sim_modes.get_current_handler().get_movement_parameters()
        return {'separation_weight': 2.0, 'alignment_weight': 0.1, 'cohesion_weight': 0.1}
    
    def _get_attack_movement_params(self):
        """Get movement parameters for attack behavior"""
        if self.sim_modes:
            return self.sim_modes.get_current_handler().get_movement_parameters()
        return {'separation_weight': 1.5, 'alignment_weight': 0.1, 'cohesion_weight': 0.1}
    
    def _get_return_movement_params(self):
        """Get movement parameters for return behavior"""
        return {'separation_weight': 0.5, 'alignment_weight': 0.0, 'cohesion_weight': 0.0}