"""Simulation controller for managing the drone simulation"""
import time
import numpy as np
from typing import List, Optional

class SimulationController:
    """Main controller for the drone simulation"""
    
    def __init__(self):
        self.running = False
        self.paused = False
        self.start_time = None
        self.simulation_time = 0.0
        self.time_scale = 1.0
        
        # Simulation objects
        self.drones = []
        self.targets = []
        self.obstacles = []
        self.missiles = []
        
        # Statistics
        self.frame_count = 0
        self.total_runtime = 0.0
        
    def start_simulation(self):
        """Start the simulation"""
        self.running = True
        self.paused = False
        self.start_time = time.time()
        
    def pause_simulation(self):
        """Pause the simulation"""
        self.paused = True
        
    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
        self.paused = False
        
    def update(self, dt):
        """Update the simulation by one time step"""
        if not self.running or self.paused:
            return
        
        self.simulation_time += dt
        self.frame_count += 1
        
    def add_drone(self, drone):
        """Add a drone to the simulation"""
        self.drones.append(drone)
        
    def add_target(self, target):
        """Add a target to the simulation"""
        self.targets.append(target)
        
    def get_statistics(self):
        """Get simulation statistics"""
        return {
            'running': self.running,
            'simulation_time': self.simulation_time,
            'frame_count': self.frame_count,
            'drones_count': len(self.drones),
            'targets_count': len(self.targets)
        }


    
    def add_target_destroyed_callback(self, callback):
        """Add callback for when target is destroyed"""
        if not hasattr(self, 'target_destroyed_callbacks'):
            self.target_destroyed_callbacks = []
        self.target_destroyed_callbacks.append(callback)
    
    def remove_target_destroyed_callback(self, callback):
        """Remove target destroyed callback"""
        if hasattr(self, 'target_destroyed_callbacks') and callback in self.target_destroyed_callbacks:
            self.target_destroyed_callbacks.remove(callback)
    
    def _trigger_target_destroyed(self, target):
        """Trigger all target destroyed callbacks"""
        if hasattr(self, 'target_destroyed_callbacks'):
            for callback in self.target_destroyed_callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"Error in target destroyed callback: {e}")
    
    def update_simulation_step(self):
        """Update one simulation step"""
        if not self.running or self.paused:
            return
        
        dt = 0.016  # ~60 FPS
        self.update(dt)
        
        # Check for target destruction
        for target in self.targets[:]:
            if hasattr(target, 'destroyed') and target.destroyed:
                self._trigger_target_destroyed(target)
                self.targets.remove(target)
    
    def check_missile_explosions(self):
        """Check for missile explosions and handle effects"""
        for missile in self.missiles[:]:
            if hasattr(missile, 'exploded') and missile.exploded:
                # Handle explosion effects
                explosion_pos = getattr(missile, 'position', (0, 0))
                explosion_radius = getattr(missile, 'explosion_radius', 50)
                
                # Check if explosion hits targets
                for target in self.targets:
                    if hasattr(target, 'position'):
                        target_pos = target.position
                        distance = ((explosion_pos[0] - target_pos[0])**2 + 
                                  (explosion_pos[1] - target_pos[1])**2)**0.5
                        
                        if distance <= explosion_radius:
                            if hasattr(target, 'destroy_target'):
                                target.destroy_target()
                            elif hasattr(target, 'destroyed'):
                                target.destroyed = True
                            self._trigger_target_destroyed(target)
                
                # Remove exploded missile
                self.missiles.remove(missile)
    
    def reset_simulation(self):
        """Reset the simulation to initial state"""
        self.stop_simulation()
        self.simulation_time = 0.0
        self.frame_count = 0
        self.total_runtime = 0.0
        
        # Clear all objects
        self.drones.clear()
        self.targets.clear() 
        self.obstacles.clear()
        self.missiles.clear()
        
        # Clear callbacks
        if hasattr(self, 'target_destroyed_callbacks'):
            self.target_destroyed_callbacks.clear()
        
        print("🔄 Simulation reset")

# Legacy alias
class MainController(SimulationController):
    pass