from PyQt5.QtCore import QObject

class UpdateGUI(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def _update_simulation(self):
        if not self.main_window.simulation_running:
            return
        self.main_window.simulation_controller.update_simulation_step()
        self.main_window.simulation_controller.check_missile_explosions()
        self.main_window._update_missile_display()
        self._update_panels()
        self.main_window._check_for_alerts()
        self.main_window.simulation_canvas.update()

    def _update_missile_display(self):
        for drone, label in zip(self.main_window.sim_manager.drones, self.main_window.missile_status_labels):
            # ...existing code...
            pass

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
