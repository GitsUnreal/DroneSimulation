from DroneSystem.States.DroneStateManager import DroneStateManager
from GUI.Objects.MissileGUI import update_missiles
from Config.SimulationConfig import SimulationConfig

class SimulationController:
    """Controls simulation logic separate from GUI"""
    
    def __init__(self, sim_manager, radar_renderer, status_checker, explosion_manager, screen_flash):
        self.sim_manager = sim_manager
        self.radar_renderer = radar_renderer
        self.status_checker = status_checker
        self.explosion_manager = explosion_manager
        self.screen_flash = screen_flash
        self.target_destroyed_callbacks = []
        self.simulation_step = 0  # <-- Add this line
    
    def add_target_destroyed_callback(self, callback):
        """Add callback for when target is destroyed"""
        self.target_destroyed_callbacks.append(callback)
    
    def update_simulation_step(self):
        """Execute one simulation step"""
        # Handle collisions
        self.sim_manager.handle_collisions()
        
        # Update radar and detect obstacles
        detected_obstacles = self.radar_renderer.update_radar(
            self.sim_manager.obstacles,
            self.sim_manager.target, 
            self.sim_manager.drones
        )
        
        # Update drone AI
        update_result = self.sim_manager.movement_controller.update_drones(self.simulation_step)
        self.simulation_step += 1  # <-- Increment step each update
        
        # Update missiles
        update_missiles(self.sim_manager.drones)
        
        # Handle target destruction
        if update_result and update_result.get('target_destroyed'):
            self._handle_target_destroyed()
        
        # Run status checks
        self.status_checker.run_periodic_checks(
            self.sim_manager.drones, 
            self.sim_manager.obstacles, 
            None  # No simulation toggle callback here
        )
        
        # Update effects
        dt = 0.05
        self.explosion_manager.update(dt)
        self.screen_flash.update(dt)
        
        return update_result
    
    def _handle_target_destroyed(self):
        """Handle target destruction"""
        # Mark all active drones to return to base
        for drone in self.sim_manager.drones:
            if drone.alive and not (hasattr(drone, 'has_landed') and drone.has_landed):
                if not hasattr(drone, 'returning_to_base'):
                    drone.has_attacked = True
        
        # Trigger screen flash
        self.screen_flash.trigger_flash(0.8)
        
        # Notify callbacks
        for callback in self.target_destroyed_callbacks:
            callback()
    
    def reset_simulation(self):
        """Reset simulation state"""
        base_center = (
            self.sim_manager.base.x() + self.sim_manager.base.width() / 2,
            self.sim_manager.base.y() + self.sim_manager.base.height() / 2
        )
        
        # Reset drones using state manager
        DroneStateManager.reset_drones_to_safe_positions(
            self.sim_manager.drones, 
            self.sim_manager.obstacles, 
            base_center
        )
        
        # Reset target
        if self.sim_manager.target:
            self.sim_manager.target.destroyed = False
    
    def check_missile_explosions(self):
        """Check for missile explosions and create effects"""
        if not hasattr(self.sim_manager.movement_controller, 'missile_manager'):
            return
        
        missile_manager = self.sim_manager.movement_controller.missile_manager
        active_missiles = missile_manager.get_active_missiles()
        
        for missile in active_missiles:
            if self._should_create_explosion(missile):
                # Use missile's explosion radius and type
                explosion_radius = getattr(missile.config, 'explosion_radius', 50.0)
                missile_type = getattr(missile, 'missile_type', 'standard')
                
                self.explosion_manager.add_explosion(
                    missile.position[0], 
                    missile.position[1], 
                    intensity=1.5,
                    radius=explosion_radius,
                    missile_type=missile_type.value if hasattr(missile_type, 'value') else missile_type
                )
                
                # Scale screen flash by explosion size
                flash_intensity = 0.3 * (explosion_radius / 50.0)
                self.screen_flash.trigger_flash(min(flash_intensity, 1.0))
                missile.explosion_triggered = True
    
    def _should_create_explosion(self, missile):
        """Check if missile should create explosion effect"""
        if hasattr(missile, 'explosion_triggered'):
            return False
        
        return (
            (hasattr(missile, 'state') and missile.state.value == 'exploding') or
            (hasattr(missile, 'hit_target') and missile.hit_target)
        )