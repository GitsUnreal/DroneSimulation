"""
Menu bar and file operations management
"""
from PyQt5.QtWidgets import QMenuBar
from DroneSystem.MainController import MainController
from GUI.Components.UIComponentManager import UIComponentManager

class MenuManager:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def create_file_menu(self):
        """Create and setup the file menu"""
        menubar = self.main_window.menuBar()
        file_menu = menubar.addMenu('File')
        
        # Save action
        save_action = file_menu.addAction('Save Simulation')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.main_window.save_load_manager.save_simulation)
        
        # Load action
        load_action = file_menu.addAction('Load Simulation')
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.main_window.save_load_manager.load_simulation)
        
        file_menu.addSeparator()
        
        # Quick save/load
        quick_save_action = file_menu.addAction('Quick Save')
        quick_save_action.setShortcut('F5')
        quick_save_action.triggered.connect(self.quick_save)
        
        quick_load_action = file_menu.addAction('Quick Load')
        quick_load_action.setShortcut('F9')
        quick_load_action.triggered.connect(self.quick_load)
        
    def quick_save(self):
        """Quick save to default file"""
        self.main_window.save_load_manager.save_simulation('quicksave.sim')
        
    def quick_load(self):
        """Quick load from default file"""
        self.main_window.save_load_manager.load_simulation('quicksave.sim')
        self._reinitialize_after_load()
        
    def _reinitialize_after_load(self):
        """Reinitialize controllers and UI after loading"""
        # Reinitialize controllers
        self.main_window.movement_controller = MainController(
            self.main_window.sim_manager.drones, 
            self.main_window.sim_manager.obstacles,
            self.main_window.sim_manager.target, 
            self.main_window.sim_manager.base, 
            self.main_window.sim_modes,
            alert_system=self.main_window.alert_system
        )
        self.main_window.sim_manager.movement_controller = self.main_window.movement_controller
        
        # Update missile status labels
        for label in self.main_window.missile_status_labels:
            label.deleteLater()
        self.main_window.missile_status_labels = UIComponentManager.create_missile_status_labels(
            self.main_window.sim_manager.drones, 
            self.main_window.missile_status_layout
        )
        
        # Update panels
        self.main_window.panel_controller.update_all_panels()
