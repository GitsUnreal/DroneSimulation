"""
UI event handling and callbacks
"""
from GUI.Components.UIComponentManager import UIComponentManager
from Factory.TargetFactory import TargetFactory
from DroneSystem.MainController import MainController

class UIEventHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def get_ui_callbacks(self):
        """Get all UI callback functions"""
        return {
            'toggle_simulation': self.toggle_simulation,
            'reset_simulation': self.reset_simulation,
            'toggle_grid': self.toggle_grid,
            'toggle_paths': self.toggle_paths,
            'toggle_debug': self.toggle_debug,
            'toggle_statistics': self.toggle_statistics,
            'toggle_performance': self.toggle_performance,
            'toggle_radar': self.toggle_radar,
            'change_mode': self.change_mode,
            'change_radar_speed': self.change_radar_speed
        }
    
    def toggle_simulation(self):
        """Toggle simulation running state"""
        self.main_window.simulation_running = not self.main_window.simulation_running
        if self.main_window.simulation_running:
            self.main_window.timer.start()
            self.main_window.buttons['start_button'].setText("Pause Simulation")
        else:
            self.main_window.timer.stop()
            self.main_window.buttons['start_button'].setText("Start Simulation")

    def toggle_grid(self):
        """Toggle grid display"""
        self.main_window.show_grid = not self.main_window.show_grid
        UIComponentManager.update_button_style(
            self.main_window.buttons['grid_button'], 
            self.main_window.show_grid, 
            'grid_button'
        )

    def toggle_paths(self):
        """Toggle path display"""
        self.main_window.show_paths = not self.main_window.show_paths
        UIComponentManager.update_button_style(
            self.main_window.buttons['path_button'], 
            self.main_window.show_paths, 
            'path_button'
        )

    def toggle_debug(self):
        """Toggle debug panel"""
        self.main_window.panel_controller.toggle_debug_panel()

    def toggle_radar(self):
        """Toggle radar display"""
        radar_enabled = self.main_window.radar_renderer.toggle_radar()
        UIComponentManager.update_button_style(
            self.main_window.buttons['radar_button'], 
            radar_enabled, 
            'radar_button'
        )

    def toggle_performance(self):
        """Toggle performance panel"""
        self.main_window.panel_controller.toggle_performance_panel()

    def toggle_statistics(self):
        """Toggle statistics panel"""
        self.main_window.panel_controller.toggle_statistics_panel()

    def reset_simulation(self):
        """Reset the entire simulation"""
        self.main_window.simulation_controller.reset_simulation()
        
        # Clear existing labels
        for label in self.main_window.missile_status_labels:
            label.deleteLater()
        
        # Recreate target and controller
        self.main_window.sim_manager.target = TargetFactory.create_random_target(
            self.main_window.sim_manager.obstacles
        )
        self.main_window.movement_controller = MainController(
            self.main_window.sim_manager.drones, 
            self.main_window.sim_manager.obstacles, 
            self.main_window.sim_manager.target, 
            self.main_window.sim_manager.base,
            self.main_window.sim_modes,
            alert_system=self.main_window.alert_system
        )
        self.main_window.sim_manager.movement_controller = self.main_window.movement_controller
        
        # Reset mission complete flag
        self.main_window.movement_controller.mission_complete_alerted = False
        
        # Recreate labels
        self.main_window.missile_status_labels = UIComponentManager.create_missile_status_labels(
            self.main_window.sim_manager.drones, 
            self.main_window.missile_status_layout
        )

    def change_mode(self, mode_text):
        """Handle mode changes"""
        from SimMode.Modes import Modes
        
        for mode in Modes:
            if mode.value == mode_text:
                self.main_window.sim_modes.set_mode(mode)
                
                # Recreate movement controller with new mode
                self.main_window.movement_controller = MainController(
                    self.main_window.sim_manager.drones,
                    self.main_window.sim_manager.obstacles,
                    self.main_window.sim_manager.target,
                    self.main_window.sim_manager.base,
                    self.main_window.sim_modes,
                    alert_system=self.main_window.alert_system
                )
                self.main_window.sim_manager.movement_controller = self.main_window.movement_controller
                
                # Apply mode rules
                self.main_window.sim_modes.apply_mode_to_simulation(
                    self.main_window.sim_manager.drones, 
                    self.main_window.sim_manager.target
                )
                
                # Update UI for new mode
                self._update_mode_ui(mode)
                break

    def _update_mode_ui(self, mode):
        """Update UI elements based on mode"""
        # Update missile status labels
        for label in self.main_window.missile_status_labels:
            label.deleteLater()
        self.main_window.missile_status_labels = UIComponentManager.create_missile_status_labels(
            self.main_window.sim_manager.drones, 
            self.main_window.missile_status_layout
        )
        
        # Force panel updates
        self.main_window.panel_controller.update_all_panels()

    def change_radar_speed(self, speed_text):
        """Handle radar speed changes"""
        speed_mapping = {
            "Slow": "slow",
            "Normal": "normal", 
            "Fast": "fast",
            "Very Fast": "very_fast",
            "Ultra Fast": "ultra_fast"
        }
        
        speed_mode = speed_mapping.get(speed_text, "normal")
        self.main_window.radar_renderer.set_sweep_speed(speed_mode)
