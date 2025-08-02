from PyQt5.QtCore import QObject
from GUI.Components.UIComponentManager import UIComponentManager


from PyQt5.QtCore import QObject
from GUI.Components.UIComponentManager import UIComponentManager

class Toggle(QObject):
    def __init__(self, main_window):
        super().__init__()
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
            UIComponentManager.update_button_style(
                mw.buttons['paths_button'], 
                mw.canvas.show_paths, 
                'paths_button'
            )
        mw.canvas.update()

    def toggle_debug(self):
        mw = self.main_window
        mw.show_debug = not mw.show_debug
        UIComponentManager.update_button_style(mw.buttons['debug_button'], mw.show_debug, 'debug_button')
        if mw.show_debug:
            mw.debug_panel.create_panel()
        else:
            mw.debug_panel.hide_panel()

