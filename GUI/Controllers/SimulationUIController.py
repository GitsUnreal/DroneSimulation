"""
Simulation-specific UI logic and updates
"""
from GUI.Components.UIComponentManager import UIComponentManager

class SimulationUIController:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def update_simulation_step(self):
        """Handle a single simulation update step"""
        if not self.main_window.simulation_running:
            return
        
        # Update simulation controller
        result = self.main_window.simulation_controller.update_simulation()
        
        # Check for target destruction
        if result.get('target_destroyed', False):
            self.main_window.simulation_running = False
            self.main_window.timer.stop()
            self.main_window.buttons['start_button'].setText("Start Simulation")
        
        # Update missile display
        self._update_missile_display()
        
        # Update panels if visible
        self.main_window.panel_controller.update_all_panels()
        
        # Force canvas repaint
        self.main_window.simulation_canvas.update()
    
    def _update_missile_display(self):
        """Update missile status display"""
        try:
            UIComponentManager.update_missile_status_labels(
                self.main_window.missile_status_labels,
                self.main_window.sim_manager.drones
            )
        except Exception as e:
            print(f"Error updating missile display: {e}")
