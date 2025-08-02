from GUI.Components.UIComponentManager import UIComponentManager
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from SimMode.Modes import Modes

def change_mode(self, mode_text):
    """Handle mode changes"""
    try:
        # Map GUI text to mode enum
        mode_mapping = {
            "Normal": Modes.NORMAL,
            "Search and Destroy": Modes.SEARCH_AND_DESTROY,
            "Escort": Modes.ESCORT,
            "Reconnaissance": Modes.RECONNAISSANCE,
            "Defensive": Modes.DEFENSIVE,
            "Bombing Run": Modes.BOMBING_RUN,
            "Patrol": Modes.PATROL,
            "Search and Rescue": Modes.SEARCH_AND_RESCUE
        }
        
        mode = mode_mapping.get(mode_text, Modes.NORMAL)
        
        if self.sim_modes:
            self.sim_modes.set_mode(mode)
            handler = self.sim_modes.get_current_handler()
            
            # Configure drones for the new mode
            if self.sim_manager and self.sim_manager.drones:
                handler.configure_drones(self.sim_manager.drones)
            
            # Configure target for the new mode
            if self.sim_manager and self.sim_manager.target:
                handler.configure_target(self.sim_manager.target)
            
            # Set radar sweep speed based on mode
            radar_speeds = {
                "normal_mode": "normal",
                "search_and_destroy": "fast",
                "escort": "normal",
                "reconnaissance": "slow",
                "defensive": "normal",
                "bombing_run": "fast",
                "patrol": "normal",
                "search_and_rescue": "fast",
            }
            mode_key = getattr(handler, "mode_name", mode.value)
            sweep_speed = radar_speeds.get(mode_key, "normal")
            self.radar_renderer.set_sweep_speed(sweep_speed)
            
    except Exception as e:
        pass