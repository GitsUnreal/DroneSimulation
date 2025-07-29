from PyQt5.QtCore import QObject
from GUI.Components.UIComponentManager import UIComponentManager

class Toggle:
    def __init__(self, main_window):
        self.main_window = main_window

    def toggle_simulation(self):
        mw = self.main_window
        mw.simulation_running = not mw.simulation_running
        if mw.simulation_running:
            mw.timer.start()
            mw.buttons['start_button'].setText("Pause Simulation")
        else:
            mw.timer.stop()
            mw.buttons['start_button'].setText("Start Simulation")

    def toggle_grid(self):
        mw = self.main_window
        if hasattr(mw.canvas, 'show_grid'):
            mw.canvas.show_grid = not mw.canvas.show_grid
        else:
            mw.canvas.show_grid = True
        if hasattr(mw, 'buttons') and 'grid_button' in mw.buttons:
            from GUI.Components.UIComponentManager import UIComponentManager
            UIComponentManager.update_button_style(
                mw.buttons['grid_button'], 
                mw.canvas.show_grid, 
                'grid_button'
            )
        mw.canvas.update()

    def toggle_paths(self):
        mw = self.main_window
        if hasattr(mw.canvas, 'show_paths'):
            mw.canvas.show_paths = not mw.canvas.show_paths
        else:
            mw.canvas.show_paths = True
        if hasattr(mw, 'buttons') and 'paths_button' in mw.buttons:
            from GUI.Components.UIComponentManager import UIComponentManager
            UIComponentManager.update_button_style(
                mw.buttons['paths_button'], 
                mw.canvas.show_paths, 
                'paths_button'
            )
        mw.canvas.update()

    def toggle_debug(self):
        mw = self.main_window
        mw.show_debug = not mw.show_debug
        from GUI.Components.UIComponentManager import UIComponentManager
        UIComponentManager.update_button_style(mw.buttons['debug_button'], mw.show_debug, 'debug_button')
        if mw.show_debug:
            mw.debug_panel.create_panel()
        else:
            mw.debug_panel.hide_panel()


class Toggle(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def toggle_simulation(self):
        self.simulation_running = not self.simulation_running
        if self.simulation_running:
            self.timer.start()
            self.buttons['start_button'].setText("Pause Simulation")
        else:
            self.timer.stop()
            self.buttons['start_button'].setText("Start Simulation")

    def toggle_grid(self):
        # Move logic from MainWindow.toggle_grid here
        if hasattr(self.main_window, 'show_grid'):
            self.main_window.show_grid = not self.main_window.show_grid
            self.main_window.simulation_canvas.update()

    def toggle_paths(self):
        """Toggle path display"""
        if hasattr(self.canvas, 'show_paths'):
            self.canvas.show_paths = not self.canvas.show_paths
        else:
            self.canvas.show_paths = True
        
        # Update button style to show active state
        if hasattr(self, 'buttons') and 'paths_button' in self.buttons:
            UIComponentManager.update_button_style(
                self.buttons['paths_button'], 
                self.canvas.show_paths, 
                'paths_button'
            )
        
        self.canvas.update()

    def toggle_debug(self):
        self.show_debug = not self.show_debug
        UIComponentManager.update_button_style(self.buttons['debug_button'], self.show_debug, 'debug_button')
        
        if self.show_debug:
            self.debug_panel.create_panel()
        else:
            self.debug_panel.hide_panel()
