
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QLabel, QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtGui import QPainter, QBrush, QColor, QPaintEvent
import os
from datetime import datetime
import json

from GUI.Components.UIComponentManager import UIComponentManager
from GUI.Simulation.SimulationManager import SimulationManager
from GUI.Panels.DebugPanel import DebugPanel
from GUI.Simulation.StatusChecker import StatusChecker
from GUI.Renderer.Renderer import Renderer
from GUI.Panels.PerformancePanel import PerformancePanel
from GUI.Panels.StatisticsPanel import StatisticsPanel
from GUI.System.AlertSystem import AlertSystem
from GUI.Renderer.MissileRenderer import MissileRenderer
from GUI.Renderer.RadarRenderer import RadarRenderer
from GUI.Effects.ExplosionEffects import ExplosionManager, ScreenFlash
from DroneSystem.Simulation.SimulationController import SimulationController
from DroneSystem.States.DroneStateManager import DroneStateManager
from DroneSystem.MainController import MainController
from Config.SimulationConfig import SimulationConfig
from SimMode.Modes import SimModes, Modes
from Factory.TargetFactory import TargetFactory
from Factory.ObstacleFactory import ObstacleFactory
from Utils.SaveLoadManager import SaveLoadManager
from GUI.Canvas.SimulationCanvas import SimulationCanvas
from GUI.Controllers.PanelController import PanelController
from GUI.Scenario.ScenarioEditor import ScenarioEditor
from GUI.System.Zoom import Zoom
from GUI.Components.CreateFile import create_file_menu
from GUI.Panels.Toggle import Toggle
from GUI.Simulation.UpdateGUI import UpdateGUI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_components()
        self._init_ui()
        self._init_simulation()
        self.save_load_manager = SaveLoadManager(self.movement_controller)
        self.file_menu_helper = create_file_menu(main_window=self)
        self.toggle_helper = Toggle(self)
        self.update_gui_helper = UpdateGUI(self)


    def _init_window(self):
        self.setWindowTitle("Drone Simulator")
        self.resize(SimulationConfig.WINDOW_WIDTH, SimulationConfig.WINDOW_HEIGHT)
        self.setStyleSheet("background-color: #f0f0f0;")

    def _init_components(self):
        self.sim_manager = SimulationManager()
        self.sim_modes = SimModes()
        self.explosion_manager = ExplosionManager()
        self.screen_flash = ScreenFlash()
        self.renderer = Renderer()
        self.missile_renderer = MissileRenderer()
        self.radar_renderer = RadarRenderer()
        self.radar_renderer.enable_radar(True)
        self.radar_renderer.radar_enabled = True
        self.debug_panel = DebugPanel(self)
        self.performance_panel = PerformancePanel(self)
        self.statistics_panel = StatisticsPanel(self)
        self.alert_system = AlertSystem(self)
        self.status_checker = StatusChecker()
        self.panel_controller = PanelController(self)
        self.simulation_controller = SimulationController(
            self.sim_manager, self.radar_renderer, self.status_checker,
            self.explosion_manager, self.screen_flash
        )
        self.simulation_controller.add_target_destroyed_callback(self._on_target_destroyed)
        self.simulation_running = False
        self.show_grid = False
        self.show_paths = False
        self.show_debug = False
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_simulation)
        self.timer.setInterval(SimulationConfig.TIMER_INTERVAL)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        callbacks = self._get_ui_callbacks()
        try:
            control_bar, self.buttons, self.mode_combo, self.speed_combo = UIComponentManager.create_control_bar(callbacks)
            main_layout.addLayout(control_bar)
        except Exception as e:
            print(f"Error creating control bar: {e}")
            start_button = QPushButton("Start")
            start_button.clicked.connect(self.toggle_simulation)
            main_layout.addWidget(start_button)
        zoom_layout = QHBoxLayout()
        from GUI.Canvas.ZoomableSimulationCanvas import ZoomableSimulationCanvas
        self.canvas = ZoomableSimulationCanvas(self)
        self.canvas.sim_manager = self.sim_manager
        self.canvas.renderer = self.renderer
        self.canvas.missile_renderer = self.missile_renderer
        self.canvas.radar_renderer = self.radar_renderer
        self.canvas.explosion_manager = self.explosion_manager
        self.canvas.screen_flash = self.screen_flash
        # Now that canvas is created, initialize Zoom with canvas
        self.zoom = Zoom(self.canvas)
        # Optionally, set zoom_label for display updates
        self.zoom.zoom_label = QLabel("Zoom: 100%")
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom.zoom_in)
        zoom_layout.addWidget(zoom_in_btn)
        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom.zoom_out)
        zoom_layout.addWidget(zoom_out_btn)
        reset_view_btn = QPushButton("Reset View")
        reset_view_btn.clicked.connect(self.zoom.reset_view)
        zoom_layout.addWidget(reset_view_btn)
        fit_view_btn = QPushButton("Fit to View")
        fit_view_btn.clicked.connect(self.zoom.fit_to_view)
        zoom_layout.addWidget(fit_view_btn)
        zoom_layout.addWidget(self.zoom.zoom_label)
        zoom_layout.addStretch()
        main_layout.addLayout(zoom_layout)
        main_layout.addWidget(self.canvas)
        self.simulation_canvas = self.canvas
        self.missile_status_layout = QVBoxLayout()
        main_layout.addLayout(self.missile_status_layout)

    def _get_ui_callbacks(self):
        return {
            'toggle_simulation': self.toggle_simulation,
            'reset_simulation': self.reset_simulation,
            'toggle_grid': self.toggle_grid,
            'toggle_paths': self.toggle_paths,
            'toggle_debug': self.toggle_debug,
            'toggle_statistics': self.panel_controller.toggle_statistics_panel,
            'toggle_performance': self.panel_controller.toggle_performance_panel,
            'change_mode': self.change_mode,
            'change_radar_speed': self.change_radar_speed,
            'launch_scenario_editor': self.launch_scenario_editor
        }

    def _init_simulation(self):
        self.sim_manager.drones.clear()
        self.sim_manager.obstacles.clear()
        if self.sim_manager.base is None:
            self.sim_manager.base = QRect(50, 50, SimulationConfig.BASE_SIZE, SimulationConfig.BASE_SIZE)
        try:
            from EnemySystem.Target import Target
            placeholder_target = Target(0, 0)
            placeholder_target.hidden = True
            placeholder_target.is_placeholder = True
            self.sim_manager.target = placeholder_target
        except Exception as e:
            self.sim_manager.target = None
        self.movement_controller = MainController(
            self.sim_manager.drones, 
            self.sim_manager.obstacles, 
            self.sim_manager.target, 
            self.sim_manager.base,
            self.sim_modes,
            alert_system=self.alert_system
        )
        self.sim_manager.movement_controller = self.movement_controller
        self.canvas.movement_controller = self.movement_controller
        self.missile_status_labels = []

    def _update_simulation(self):
        self.update_gui_helper._update_simulation()

    def _update_panels(self):
        self.update_gui_helper._update_panels()

    def toggle_simulation(self):
        self.toggle_helper.toggle_simulation()

    def toggle_grid(self):
        self.toggle_helper.toggle_grid()

    def toggle_paths(self):
        self.toggle_helper.toggle_paths()

    def toggle_debug(self):
        self.toggle_helper.toggle_debug()
        self.timer.setInterval(SimulationConfig.TIMER_INTERVAL)

    def change_mode(self, mode_text):
        # Use helper or implement logic here
        try:
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
                if self.sim_manager and self.sim_manager.drones:
                    handler.configure_drones(self.sim_manager.drones)
                if self.sim_manager and self.sim_manager.target:
                    handler.configure_target(self.sim_manager.target)
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

    def change_radar_speed(self, speed_text):
        speed_mapping = {
            "Slow": "slow",
            "Normal": "normal", 
            "Fast": "fast",
            "Very Fast": "very_fast",
            "Ultra Fast": "ultra_fast"
        }
        speed_mode = speed_mapping.get(speed_text, "normal")
        self.radar_renderer.set_sweep_speed(speed_mode)

    def launch_scenario_editor(self):
        try:
            self.scenario_editor = ScenarioEditor(self)
            self.scenario_editor.show()
        except Exception as e:
            print(f"Error launching scenario editor: {e}")

    # Removed duplicate/conflicting __init__ and erroneous code block

    def _get_ui_callbacks(self):
        """Get all UI callback functions"""
        return {
            'toggle_simulation': self.toggle_simulation,
            'reset_simulation': self.reset_simulation,
            'toggle_grid': self.toggle_grid,
            'toggle_paths': self.toggle_paths,
            'toggle_debug': self.toggle_debug,
            'toggle_statistics': self.panel_controller.toggle_statistics_panel,
            'toggle_performance': self.panel_controller.toggle_performance_panel,
            'change_mode': self.change_mode,
            'change_radar_speed': self.change_radar_speed,
            'launch_scenario_editor': self.launch_scenario_editor
        }

    def _init_simulation(self):
        """Initialize simulation using manager"""
        # Initialize empty simulation
        self.sim_manager.drones.clear()
        self.sim_manager.obstacles.clear()
        
        # Initialize base with default position

        
        if self.sim_manager.base is None:
            self.sim_manager.base = QRect(50, 50, SimulationConfig.BASE_SIZE, SimulationConfig.BASE_SIZE)
        
        try:
            from EnemySystem.Target import Target
            placeholder_target = Target(0, 0)
            placeholder_target.hidden = True
            placeholder_target.is_placeholder = True
            self.sim_manager.target = placeholder_target
        except Exception as e:
            self.sim_manager.target = None
    
        self.movement_controller = MainController(
            self.sim_manager.drones, 
            self.sim_manager.obstacles, 
            self.sim_manager.target, 
            self.sim_manager.base,
            self.sim_modes,
            alert_system=self.alert_system
        )
        self.sim_manager.movement_controller = self.movement_controller
        
        # Connect movement controller to canvas
        self.canvas.movement_controller = self.movement_controller
        
        # Create empty missile status labels
        self.missile_status_labels = []

    def _update_simulation(self):
        self.update_gui_helper._update_simulation()
        

    def _update_panels(self):
        """Update monitoring panels"""
        if self.show_debug:
            self.debug_panel.update_info(self.sim_manager.drones, self.sim_manager.movement_controller)
        
        if self.performance_panel.is_visible:
            self.performance_panel.update_metrics(self.sim_manager.drones, self.sim_manager.movement_controller)
        
        if self.statistics_panel.is_visible:
            self.statistics_panel.update_statistics(self.sim_manager.drones, self.sim_manager.movement_controller)

    def _check_for_alerts(self):
        """Check for events that should trigger alerts"""
        for drone in self.sim_manager.drones:
            self._check_drone_alerts(drone)

    def _check_drone_alerts(self, drone):
        """Check alerts for a specific drone"""
        if not drone.alive and not hasattr(drone, '_destruction_alerted'):
            # Remove debug print
            self.alert_system.show_drone_destroyed_alert(drone.drone_id)
            drone._destruction_alerted = True
        
        if drone.missiles_fired >= drone.max_missiles and not hasattr(drone, '_missiles_alerted'):
            # Remove debug print
            self.alert_system.show_all_missiles_fired_alert(drone.drone_id)
            drone._missiles_alerted = True
        
        if hasattr(drone, 'has_landed') and drone.has_landed and not hasattr(drone, '_landing_alerted'):
            self.alert_system.show_drone_landed_alert(drone.drone_id)
            drone._landing_alerted = True

    def _on_target_destroyed(self):
        """Handle target destroyed event"""
        self.alert_system.show_alert(
            "🎯 TARGET DESTROYED! 🎯\n\nMission Objective Complete!\nDrones returning to base...", 
            "#00FF00", 
            duration=4000
        )

    def reset_simulation(self):
        """Reset simulation to clean state"""
        try:
            # Stop any running simulation
            self.stop_simulation()
            
            # Clear simulation elements
            self.sim_manager.drones.clear()
            self.sim_manager.obstacles.clear()
            
            # Reset target to placeholder
            try:
                from EnemySystem.Target import Target
                placeholder_target = Target(0, 0)
                placeholder_target.hidden = True
                placeholder_target.is_placeholder = True
                self.sim_manager.target = placeholder_target
            except:
                self.sim_manager.target = None
            
            # Ensure base exists
            if self.sim_manager.base is None:
                from PyQt5.QtCore import QRect
                from Config.SimulationConfig import SimulationConfig
                self.sim_manager.base = QRect(50, 50, getattr(SimulationConfig, 'BASE_SIZE', 20), getattr(SimulationConfig, 'BASE_SIZE', 20))
            
            # Clear missile status labels
            for label in self.missile_status_labels:
                label.deleteLater()
            self.missile_status_labels = []
            
            # Update canvas
            self.canvas.update()
            
        except Exception as e:
            pass

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
        self.radar_renderer.set_sweep_speed(speed_mode)

    def reset_simulation(self):
        """Reset simulation to clean state"""
        try:
            # Stop any running simulation
            self.stop_simulation()
            
            # Clear simulation elements
            self.sim_manager.drones.clear()
            self.sim_manager.obstacles.clear()
            
            # Reset target to placeholder
            try:
                from EnemySystem.Target import Target
                placeholder_target = Target(0, 0)
                placeholder_target.hidden = True
                placeholder_target.is_placeholder = True
                self.sim_manager.target = placeholder_target
            except:
                self.sim_manager.target = None
            
            # Ensure base exists
            if self.sim_manager.base is None:
                from PyQt5.QtCore import QRect
                from Config.SimulationConfig import SimulationConfig
                self.sim_manager.base = QRect(50, 50, getattr(SimulationConfig, 'BASE_SIZE', 20), getattr(SimulationConfig, 'BASE_SIZE', 20))
            
            # Clear missile status labels
            for label in self.missile_status_labels:
                label.deleteLater()
            self.missile_status_labels = []
            
            # Update canvas
            self.canvas.update()
            
        except Exception as e:
            pass

    def spawn_convoy_targets(self, count=5):
        """Spawn a convoy of targets"""
        self.sim_manager.targets = [
            TargetFactory.create_random_target(self.sim_manager.obstacles)
            for _ in range(count)
        ]
        # Apply mode rules to all targets
        self.sim_modes.apply_mode_to_simulation(self.sim_manager.drones, self.sim_manager.targets)
        # Update movement controller
        self.movement_controller = MainController(
            self.sim_manager.drones, self.sim_manager.obstacles,
            self.sim_manager.targets, self.sim_manager.base, self.sim_modes,
            alert_system=self.alert_system  # <-- ADD THIS LINE
        )
        self.sim_manager.movement_controller = self.movement_controller

    def get_current_drone_count(self):
        """Get current number of drones in simulation"""
        return len(self.sim_manager.drones)

    def update_drone_count_display(self):
        """Update UI to show current drone count"""
        current_count = self.get_current_drone_count()
        
        # Update window title to show drone count
        self.setWindowTitle(f"Drone Simulator - {current_count} Drones")
        
        # You could also add a label to show this info
        if hasattr(self, 'drone_count_label'):
            self.drone_count_label.setText(f"Drones: {current_count}")

    def _update_panels(self):
        self.update_gui_helper._update_panels()


