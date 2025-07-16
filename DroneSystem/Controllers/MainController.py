from .MovementController import MovementController
from .CombatController import CombatController
from .StateController import StateController
from ..AI.BehaviorEngine import BehaviorEngine

class MainController:
    def __init__(self, drones, obstacles=None, target=None, base=None, sim_modes=None, alert_system=None):
        self.drones = drones
        self.obstacles = obstacles or []
        self.target = target
        self.base = base
        self.sim_modes = sim_modes
        self.alert_system = alert_system
        
        # Initialize sub-controllers
        self.movement_controller = MovementController(drones, obstacles, base)
        self.combat_controller = CombatController(target, alert_system)
        self.state_controller = StateController(drones, base, alert_system)
        self.behavior_engine = BehaviorEngine(sim_modes)
        
        self.simulation_speed = 1.0
        self.mission_complete_alerted = False
    
    def update_drones(self, simulation_step=0):
        """Orchestrate all drone updates through specialized controllers"""
        # Update target movement if applicable
        if self.target and hasattr(self.target, 'is_moving_target') and self.target.is_moving_target:
            self.target.update_movement()
            self.combat_controller.update_target(self.target)
        
        # Update missiles first
        target_hit = self.combat_controller.update_missiles(self.drones, self.obstacles)
        if target_hit:
            return {'target_destroyed': True}
        
        # Process each active drone
        for drone in self.drones:
            if self.state_controller.should_skip_drone(drone):
                continue
                
            # Determine drone behavior based on current mode and state
            behavior = self.behavior_engine.get_drone_behavior(drone, self.target, simulation_step)
            
            # Execute movement
            self.movement_controller.update_drone_movement(drone, behavior, simulation_step)
            
            # Handle combat actions
            self.combat_controller.handle_drone_combat(drone, self.target)
            
            # Update drone state
            self.state_controller.update_drone_state(drone, self.base)
        
        # Handle alerts and mission completion
        self._handle_alerts()
        
        return {'target_destroyed': False}
    
    def _handle_alerts(self):
        """Handle all alert notifications"""
        self.state_controller.process_alerts()
        
        if self.state_controller.is_mission_complete() and not self.mission_complete_alerted:
            self.alert_system.show_mission_complete_alert(self.drones)
            self.mission_complete_alerted = True