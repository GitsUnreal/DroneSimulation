def export_current_simulation_as_scenario(self):
        """Export current simulation state as a scenario"""
        scenario_data = {
            'metadata': {
                'name': f"Exported Scenario {len(self.sim_manager.drones)} drones",
                'mission_type': self.sim_modes.current_mode.value.lower(),
                'difficulty': 'Normal',
                'time_limit': 300,
                'map_width': 1080,
                'map_height': 720,
                'grid_size': 20
            },
            'items': []
        }
        
        # Export drones
        for i, drone in enumerate(self.sim_manager.drones):
            scenario_data['items'].append({
                'type': 'drone',
                'position': [int(drone.position[0]), int(drone.position[1])],
                'properties': {
                    'drone_id': i,
                    'max_missiles': drone.max_missiles,
                    'formation_role': 'assault'
                }
            })
        
        # Export target
        if self.sim_manager.target:
            scenario_data['items'].append({
                'type': 'target',
                'position': [int(self.sim_manager.target.position[0]), int(self.sim_manager.target.position[1])],
                'properties': {
                    'target_type': 'standard',
                    'health': getattr(self.sim_manager.target, 'health', 100),
                    'hidden': getattr(self.sim_manager.target, 'hidden', False)
                }
            })
        
        # Export obstacles
        for obstacle in self.sim_manager.obstacles:
            scenario_data['items'].append({
                'type': 'obstacle',
                'position': [obstacle.x, obstacle.y],
                'properties': {
                    'size': getattr(obstacle, 'size', 40),
                    'destructible': False
                }
            })
        
        # Export base
        scenario_data['items'].append({
            'type': 'base',
            'position': [self.sim_manager.base.x(), self.sim_manager.base.y()],
            'properties': {
                'capacity': 10
            }
        })
        
        return scenario_data