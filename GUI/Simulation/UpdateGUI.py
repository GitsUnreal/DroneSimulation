from PyQt5.QtCore import QObject

from DroneSystem.States.DroneStateManager import DroneStateManager

class UpdateGUI(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def _update_simulation(self):
        if not self.main_window.simulation_running:
            return
        self.main_window.simulation_controller.update_simulation_step()
        self.main_window.simulation_controller.check_missile_explosions()
        self._update_missile_display()
        self._update_panels()
        self.main_window._check_for_alerts()
        self.main_window.simulation_canvas.update()

    def _update_missile_display(self):
        """Update missile status display"""
        for drone, label in zip(self.main_window.sim_manager.drones, self.main_window.missile_status_labels):
            status_info = DroneStateManager.get_drone_status_info(drone)
            label.setText(status_info['text'])
            label.setStyleSheet(
                f"font-size: 12px; color: {status_info['color']}; "
                f"background-color: rgba(255,255,255,150); padding: 2px; border-radius: 3px;"
            )


    def _update_panels(self):
        if self.main_window.show_debug:
            if hasattr(self.main_window.debug_panel, 'update_info'):
                self.main_window.debug_panel.update_info(self.main_window.sim_manager.drones, self.main_window.movement_controller)
        if self.main_window.performance_panel.is_visible:
            if hasattr(self.main_window.performance_panel, 'update_metrics'):
                self.main_window.performance_panel.update_metrics(self.main_window.sim_manager.drones, self.main_window.movement_controller)
        if self.main_window.statistics_panel.is_visible:
            if hasattr(self.main_window.statistics_panel, 'update_statistics'):
                self.main_window.statistics_panel.update_statistics(self.main_window.sim_manager.drones, self.main_window.movement_controller)
