"""
Panel visibility and update management
"""
from GUI.Components.UIComponentManager import UIComponentManager

class PanelController:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def toggle_debug_panel(self):
        """Toggle debug panel visibility"""
        self.main_window.show_debug = not self.main_window.show_debug
        UIComponentManager.update_button_style(
            self.main_window.buttons['debug_button'], 
            self.main_window.show_debug, 
            'debug_button'
        )
        
        if self.main_window.show_debug:
            self.main_window.debug_panel.create_panel()
        else:
            self.main_window.debug_panel.hide_panel()

    def toggle_performance_panel(self):
        """Toggle performance panel visibility"""
        if self.main_window.performance_panel.is_visible:
            self.main_window.performance_panel.hide_panel()
            UIComponentManager.update_button_style(
                self.main_window.buttons['perf_button'], False, 'perf_button'
            )
        else:
            self.main_window.performance_panel.show_panel()
            UIComponentManager.update_button_style(
                self.main_window.buttons['perf_button'], True, 'perf_button'
            )
            # Force update panel after showing
            self.main_window.performance_panel.update_metrics(
                self.main_window.sim_manager.drones, 
                self.main_window.sim_manager.movement_controller
            )
            
            # Force raise the panel to front
            self.main_window.performance_panel.raise_()

    def toggle_statistics_panel(self):
        """Toggle statistics panel visibility"""
        if self.main_window.statistics_panel.is_visible:
            self.main_window.statistics_panel.hide_panel()
            UIComponentManager.update_button_style(
                self.main_window.buttons['stats_button'], False, 'stats_button'
            )
        else:
            self.main_window.statistics_panel.show_panel()
            UIComponentManager.update_button_style(
                self.main_window.buttons['stats_button'], True, 'stats_button'
            )
            # Force update panel after showing
            self.main_window.statistics_panel.update_statistics(
                self.main_window.sim_manager.drones, 
                self.main_window.sim_manager.movement_controller
            )
            
            # Force raise the panel to front
            self.main_window.statistics_panel.raise_()

    def update_all_panels(self):
        """Update all visible panels"""
        if self.main_window.show_debug:
            self.main_window.debug_panel.update_info(
                self.main_window.sim_manager.drones, 
                self.main_window.sim_manager.movement_controller
            )
        
        if self.main_window.performance_panel.is_visible:
            self.main_window.performance_panel.update_metrics(
                self.main_window.sim_manager.drones, 
                self.main_window.sim_manager.movement_controller
            )
        
        if self.main_window.statistics_panel.is_visible:
            self.main_window.statistics_panel.update_statistics(
                self.main_window.sim_manager.drones, 
                self.main_window.sim_manager.movement_controller
            )
