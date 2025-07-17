import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QLabel, QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QPaintEvent  # Add these too
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
from GUI.Windows.ScenarioEditor import ScenarioEditor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_components()
        self._init_ui()
        self._init_simulation()
        self.save_load_manager = SaveLoadManager(self.movement_controller)
        self.create_file_menu()

    def _init_window(self):
        """Initialize window properties"""
        self.setWindowTitle("Drone Simulator")
        self.resize(SimulationConfig.WINDOW_WIDTH, SimulationConfig.WINDOW_HEIGHT)
        self.setStyleSheet("background-color: #f0f0f0;")

    def _init_components(self):
        """Initialize all GUI components"""
        # Initialize simulation manager FIRST
        self.sim_manager = SimulationManager()
        
        # Initialize simulation modes
        self.sim_modes = SimModes()
        
        # Initialize effects systems
        self.explosion_manager = ExplosionManager()
        self.screen_flash = ScreenFlash()
        
        # Initialize renderers and managers
        self.renderer = Renderer()
        self.missile_renderer = MissileRenderer()
        self.radar_renderer = RadarRenderer()
        
        # ALWAYS ENABLE RADAR - no button control needed
        self.radar_renderer.enable_radar(True)
        self.radar_renderer.radar_enabled = True
        print("Radar is always enabled")
        
        # UI panels - Make sure they get the main window as parent
        self.debug_panel = DebugPanel(self)
        self.performance_panel = PerformancePanel(self)
        self.statistics_panel = StatisticsPanel(self)
        self.alert_system = AlertSystem(self)
        self.status_checker = StatusChecker()
        
        self.panel_controller = PanelController(self)
        
        # Simulation controller - NOW we can use sim_manager
        self.simulation_controller = SimulationController(
            self.sim_manager, self.radar_renderer, self.status_checker,
            self.explosion_manager, self.screen_flash
        )
        self.simulation_controller.add_target_destroyed_callback(self._on_target_destroyed)
        
        # State
        self.simulation_running = False
        self.show_grid = False
        self.show_paths = False
        self.show_debug = False
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_simulation)
        self.timer.setInterval(SimulationConfig.TIMER_INTERVAL)

    def _init_ui(self):
        """Initialize UI layout"""
        # Create central widget for QMainWindow
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Create control bar
        callbacks = self._get_ui_callbacks()
        try:
            control_bar, self.buttons, self.mode_combo, self.speed_combo = UIComponentManager.create_control_bar(callbacks)
            main_layout.addLayout(control_bar)
        except Exception as e:
            print(f"Error creating control bar: {e}")
            start_button = QPushButton("Start")
            start_button.clicked.connect(self.toggle_simulation)
            main_layout.addWidget(start_button)

        # Add zoom controls
        zoom_layout = QHBoxLayout()
        
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(zoom_out_btn)
        
        reset_view_btn = QPushButton("Reset View")
        reset_view_btn.clicked.connect(self.reset_view)
        zoom_layout.addWidget(reset_view_btn)
        
        fit_view_btn = QPushButton("Fit to View")
        fit_view_btn.clicked.connect(self.fit_to_view)
        zoom_layout.addWidget(fit_view_btn)
        
        self.zoom_label = QLabel("Zoom: 100%")
        zoom_layout.addWidget(self.zoom_label)
        
        zoom_layout.addStretch()
        main_layout.addLayout(zoom_layout)

        # Create zoomable simulation canvas
        from GUI.Canvas.ZoomableSimulationCanvas import ZoomableSimulationCanvas
        self.canvas = ZoomableSimulationCanvas(self)

        # Connect canvas to simulation components (remove movement_controller for now)
        self.canvas.sim_manager = self.sim_manager
        # self.canvas.movement_controller = self.movement_controller  # Remove this line
        self.canvas.renderer = self.renderer
        self.canvas.missile_renderer = self.missile_renderer
        self.canvas.radar_renderer = self.radar_renderer
        self.canvas.explosion_manager = self.explosion_manager
        self.canvas.screen_flash = self.screen_flash

        main_layout.addWidget(self.canvas)
        
        # Store reference for backward compatibility
        self.simulation_canvas = self.canvas

        # Create missile status layout for labels
        self.missile_status_layout = QVBoxLayout()
        main_layout.addLayout(self.missile_status_layout)

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
        from PyQt5.QtCore import QRect
        from Config.SimulationConfig import SimulationConfig
        
        if self.sim_manager.base is None:
            self.sim_manager.base = QRect(50, 50, SimulationConfig.BASE_SIZE, SimulationConfig.BASE_SIZE)
        
        # Create a placeholder target instead of None
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
        """Main simulation update loop"""
        if not self.simulation_running:
            return
        
        # Use simulation controller
        self.simulation_controller.update_simulation_step()
        self.simulation_controller.check_missile_explosions()
        
        # Update UI components
        self._update_missile_display()
        self._update_panels()
        self._check_for_alerts()
        
        # Update the canvas
        self.simulation_canvas.update()

    def _update_missile_display(self):
        """Update missile status display"""
        for drone, label in zip(self.sim_manager.drones, self.missile_status_labels):
            status_info = DroneStateManager.get_drone_status_info(drone)
            label.setText(status_info['text'])
            label.setStyleSheet(
                f"font-size: 12px; color: {status_info['color']}; "
                f"background-color: rgba(255,255,255,150); padding: 2px; border-radius: 3px;"
            )

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

    # UI Toggle Methods
    def toggle_simulation(self):
        self.simulation_running = not self.simulation_running
        if self.simulation_running:
            self.timer.start()
            self.buttons['start_button'].setText("Pause Simulation")
            # Remove all test alerts - just clean toggle
        else:
            self.timer.stop()
            self.buttons['start_button'].setText("Start Simulation")

    def toggle_grid(self):
        """Toggle grid display"""
        if hasattr(self.canvas, 'show_grid'):
            self.canvas.show_grid = not self.canvas.show_grid
        else:
            self.canvas.show_grid = True
        
        # Update button style to show active state
        if hasattr(self, 'buttons') and 'grid_button' in self.buttons:
            UIComponentManager.update_button_style(
                self.buttons['grid_button'], 
                self.canvas.show_grid, 
                'grid_button'
            )
        
        self.canvas.update()

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

    def toggle_grid(self):
        """Toggle grid display"""
        if hasattr(self.canvas, 'show_grid'):
            self.canvas.show_grid = not self.canvas.show_grid
        else:
            self.canvas.show_grid = True
        
        # Update button style to show active state
        if hasattr(self, 'buttons') and 'grid_button' in self.buttons:
            UIComponentManager.update_button_style(
                self.buttons['grid_button'], 
                self.canvas.show_grid, 
                'grid_button'
            )
        
        self.canvas.update()

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

    def create_file_menu(self):
        """Create file menu with save/load and scenario editor options"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        
        # Scenario Editor
        scenario_action = file_menu.addAction('Scenario Editor')
        scenario_action.triggered.connect(self.launch_scenario_editor)
        
        file_menu.addSeparator()
        
        # Quick Save
        quick_save_action = file_menu.addAction('Quick Save')
        quick_save_action.setShortcut('F5')
        quick_save_action.triggered.connect(self.quick_save)
        
        # Quick Load
        quick_load_action = file_menu.addAction('Quick Load')
        quick_load_action.setShortcut('F9')
        quick_load_action.triggered.connect(self.quick_load)
        
        file_menu.addSeparator()
        
        # Save Simulation
        save_action = file_menu.addAction('Save Simulation')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_simulation)
        
        # Load Simulation
        load_action = file_menu.addAction('Load Simulation')
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_simulation)

    def launch_scenario_editor(self):
        """Launch the scenario editor"""
        try:
            self.scenario_editor = ScenarioEditor(self)
            self.scenario_editor.show()
        except Exception as e:
            print(f"Error launching scenario editor: {e}")

    def quick_save(self):
        """Quick save using scenario format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quicksave_{timestamp}.scenario"
        self.save_load_manager.save_simulation(filename)

    def quick_load(self):
        """Quick load from most recent save"""
        saves_dir = "saves"
        if os.path.exists(saves_dir):
            scenario_files = [f for f in os.listdir(saves_dir) if f.endswith('.scenario')]
            if scenario_files:
                # Load most recent file
                latest_file = max(scenario_files, key=lambda f: os.path.getctime(os.path.join(saves_dir, f)))
                full_path = os.path.join(saves_dir, latest_file)
                
                try:
                    with open(full_path, 'r') as f:
                        scenario_data = json.load(f)
                    self.apply_scenario_to_simulation(scenario_data)
                    QMessageBox.information(self, "Success", f"Loaded: {latest_file}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load: {str(e)}")
            else:
                QMessageBox.warning(self, "No Saves", "No save files found")
        else:
            QMessageBox.warning(self, "No Saves", "Saves directory not found")

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

    def zoom_in(self):
        """Zoom in the simulation view"""
        if hasattr(self, 'canvas'):
            new_zoom = self.canvas.zoom_factor * 1.2
            self.canvas.zoom_factor = max(self.canvas.min_zoom, min(self.canvas.max_zoom, new_zoom))
            self.canvas.update()
            self.update_zoom_display(self.canvas.zoom_factor)

    def zoom_out(self):
        """Zoom out the simulation view"""
        if hasattr(self, 'canvas'):
            new_zoom = self.canvas.zoom_factor / 1.2
            self.canvas.zoom_factor = max(self.canvas.min_zoom, min(self.canvas.max_zoom, new_zoom))
            self.canvas.update()
            self.update_zoom_display(self.canvas.zoom_factor)

    def reset_view(self):
        """Reset the view to default zoom and position"""
        if hasattr(self, 'canvas'):
            self.canvas.reset_view()
            self.update_zoom_display(1.0)

    def fit_to_view(self):
        """Fit all simulation elements to view"""
        if hasattr(self, 'canvas'):
            self.canvas.fit_to_view()
            self.update_zoom_display(self.canvas.zoom_factor)

    def update_zoom_display(self, zoom_factor):
        """Update zoom display"""
        zoom_percent = int(zoom_factor * 100)
        if hasattr(self, 'zoom_label'):
            self.zoom_label.setText(f"Zoom: {zoom_percent}%")

    def load_scenario_from_file(self, filename: str):
        """Load a scenario from the scenario editor format"""
        try:
            import json
            with open(filename, 'r') as f:
                scenario_data = json.load(f)
            
            self.apply_scenario_to_simulation(scenario_data)
            return True
        except Exception as e:
            print(f"Failed to load scenario: {e}")
            return False

    def apply_scenario_to_simulation(self, scenario_data: dict):
        """Apply scenario data to current simulation"""
        try:
            # Ensure base exists before proceeding
            if self.sim_manager.base is None:
                from PyQt5.QtCore import QRect
                from Config.SimulationConfig import SimulationConfig
                self.sim_manager.base = QRect(50, 50, SimulationConfig.BASE_SIZE, SimulationConfig.BASE_SIZE)
        
            # Reset simulation first
            self.reset_simulation()
            
            # Apply mission settings
            metadata = scenario_data.get('metadata', {})
            mission_type = metadata.get('mission_type', 'normal').lower()
            
            # Count drones in scenario
            items = scenario_data.get('items', [])
            scenario_drones = [item for item in items if item.get('type') == 'drone']
            num_drones_in_scenario = len(scenario_drones)
            
            # Set mode
            try:
                if mission_type == 'search_and_destroy' and hasattr(Modes, 'SEARCH_AND_DESTROY'):
                    self.sim_modes.set_mode(Modes.SEARCH_AND_DESTROY)
                elif mission_type == 'escort' and hasattr(Modes, 'ESCORT'):
                    self.sim_modes.set_mode(Modes.ESCORT)
                else:
                    self.sim_modes.set_mode(Modes.NORMAL)
            except Exception as e:
                self.sim_modes.set_mode(Modes.NORMAL)
            
            # Clear existing elements
            self.sim_manager.drones.clear()
            self.sim_manager.obstacles.clear()
            
            # Process items
            drone_count = 0
            for item in items:
                try:
                    item_type = item.get('type')
                    position = item.get('position', [100, 100])
                    if isinstance(position, (int, float)):
                        position = [position, position]
                    elif not isinstance(position, (list, tuple)):
                        position = [100, 100]
                    
                    if len(position) < 2:
                        position = position + [100] * (2 - len(position))
                    
                    properties = item.get('properties', {})
                    
                    if item_type == 'drone':
                        from DroneSystem.Core.Drone import Drone
                        
                        drone = Drone(
                            position=[float(position[0]), float(position[1])], 
                            velocity=[0.0, 0.0], 
                            drone_id=drone_count
                        )
                        
                        drone.max_missiles = properties.get('max_missiles', 2)
                        drone.formation_role = properties.get('formation_role', 'assault')
                        
                        self.sim_manager.drones.append(drone)
                        drone_count += 1
                        
                    elif item_type == 'target':
                        try:
                            from EnemySystem.Target import Target
                            
                            target_x = float(position[0])
                            target_y = float(position[1])
                            
                            target = Target(
                                target_id=1, 
                                position=[target_x, target_y],
                                height=properties.get('height', 30),
                                width=properties.get('width', 30),
                                hidden=properties.get('hidden', False)
                            )
                            
                            target.target_type = properties.get('target_type', 'standard')
                            target.health = properties.get('health', 100)
                            target.movement_pattern = properties.get('movement_pattern', 'stationary')
                            
                            if mission_type == 'escort':
                                target.is_vip = True
                                target.needs_escort = True
                            
                            self.sim_manager.target = target
                            
                        except Exception as e:
                            pass
                            
                    elif item_type == 'obstacle':
                        try:
                            from PyQt5.QtCore import QRect
                            
                            obs_x = int(float(position[0]))
                            obs_y = int(float(position[1]))
                            
                            obs_width = properties.get('width', properties.get('size', 40))
                            obs_height = properties.get('height', properties.get('size', 40))
                            
                            obs_width = max(int(obs_width), 20)
                            obs_height = max(int(obs_height), 20)
                            
                            obstacle = QRect(obs_x, obs_y, obs_width, obs_height)
                            self.sim_manager.obstacles.append(obstacle)
                            
                        except Exception as e:
                            fallback_obs = QRect(300 + len(self.sim_manager.obstacles) * 60, 300, 40, 40)
                            self.sim_manager.obstacles.append(fallback_obs)
                            
                    elif item_type == 'base':
                        try:
                            from PyQt5.QtCore import QRect
                            
                            base_x = int(float(position[0]))
                            base_y = int(float(position[1]))
                            base_capacity = properties.get('capacity', 10)
                            
                            base_size = max(base_capacity, 20)
                            self.sim_manager.base = QRect(base_x, base_y, base_size, base_size)
                            
                        except Exception as e:
                            if self.sim_manager.base is None:
                                self.sim_manager.base = QRect(50, 50, 20, 20)
                
                except Exception as e:
                    continue
    
            # Reinitialize movement controller
            try:
                self.movement_controller = MainController(
                    self.sim_manager.drones, 
                    self.sim_manager.obstacles, 
                    self.sim_manager.target, 
                    self.sim_manager.base,
                    self.sim_modes,
                    alert_system=self.alert_system
                )
                self.sim_manager.movement_controller = self.movement_controller
            except Exception as e:
                pass
            
            # Recreate missile status labels
            try:
                for label in self.missile_status_labels:
                    label.deleteLater()
                self.missile_status_labels = UIComponentManager.create_missile_status_labels(
                    self.sim_manager.drones, self.missile_status_layout
                )
            except Exception as e:
                pass
            
            # Update canvas
            try:
                self.canvas.sim_manager = self.sim_manager
                self.canvas.movement_controller = self.movement_controller
                self.canvas.renderer = self.renderer
                self.canvas.missile_renderer = self.missile_renderer
                self.canvas.radar_renderer = self.radar_renderer
                self.canvas.explosion_manager = self.explosion_manager
                self.canvas.screen_flash = self.screen_flash
                
                self.canvas.show_grid = self.show_grid
                self.canvas.show_paths = self.show_paths
                self.canvas.show_debug = self.show_debug
                
                self.canvas.update()
                self.canvas.repaint()
                QApplication.processEvents()
                
            except Exception as e:
                pass
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply scenario: {str(e)}")

        # Force canvas updates
        try:
            self.canvas.setMinimumSize(800, 600)
            self.canvas.resize(1080, 720)
            
            for i in range(3):
                self.canvas.update()
                self.canvas.repaint()
                QApplication.processEvents()
                
        except Exception as e:
            pass

    def export_current_simulation_as_scenario(self):
        """Export current simulation state as a scenario"""
        scenario_data = {
            'metadata': {
                'name': f"Exported Scenario {len(self.sim_manager.drones)} drones",
                'mission_type': self.sim_modes.current_mode.value.lower(),
                'difficulty': 'Normal',
                'time_limit': 300,
                'map_width': 1080,
                'map_height': 720,
                'grid_size': 20
            },
            'items': []
        }
        
        # Export drones
        for i, drone in enumerate(self.sim_manager.drones):
            scenario_data['items'].append({
                'type': 'drone',
                'position': [int(drone.position[0]), int(drone.position[1])],
                'properties': {
                    'drone_id': i,
                    'max_missiles': drone.max_missiles,
                    'formation_role': 'assault'
                }
            })
        
        # Export target
        if self.sim_manager.target:
            scenario_data['items'].append({
                'type': 'target',
                'position': [int(self.sim_manager.target.position[0]), int(self.sim_manager.target.position[1])],
                'properties': {
                    'target_type': 'standard',
                    'health': getattr(self.sim_manager.target, 'health', 100),
                    'hidden': getattr(self.sim_manager.target, 'hidden', False)
                }
            })
        
        # Export obstacles
        for obstacle in self.sim_manager.obstacles:
            scenario_data['items'].append({
                'type': 'obstacle',
                'position': [obstacle.x, obstacle.y],
                'properties': {
                    'size': getattr(obstacle, 'size', 40),
                    'destructible': False
                }
            })
        
        # Export base
        scenario_data['items'].append({
            'type': 'base',
            'position': [self.sim_manager.base.x(), self.sim_manager.base.y()],
            'properties': {
                'capacity': 10
            }
        })
        
        return scenario_data

    def save_simulation(self):
        """Save simulation with file dialog"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Simulation", "", "Simulation Files (*.sim);;All Files (*)")
        
        if filename:
            if not filename.endswith('.sim'):
                filename += '.sim'
            
            try:
                self.save_load_manager.save_simulation(filename)
                QMessageBox.information(self, "Success", f"Simulation saved: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save simulation: {str(e)}")

    def load_simulation(self):
        """Load simulation with file dialog"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Simulation", "saves/", 
            "Scenario Files (*.scenario *.sim);;All Files (*)")  # Support both formats
    
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                print(f"Loading file: {filename}")
                print(f"File structure keys: {list(data.keys())}")
                
                # Check format and handle appropriately
                if 'metadata' in data and 'items' in data:
                    # It's already scenario format
                    print("Detected scenario format")
                    scenario_data = data
                elif 'drones' in data and 'config' in data:
                    # It's a .sim file - convert to scenario format
                    print("Detected .sim format - converting...")
                    scenario_data = self.convert_sim_to_scenario(data)
                else:
                    # Try to detect format by content
                    print("Unknown format - attempting to parse...")
                    scenario_data = self.parse_unknown_format(data)
                
                # Apply the scenario to simulation
                self.apply_scenario_to_simulation(scenario_data)
                
                QMessageBox.information(self, "Success", f"Simulation loaded: {filename}")
                
            except Exception as e:
                print(f"Error loading file: {e}")
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Error", f"Failed to load simulation: {str(e)}")

    def convert_sim_to_scenario(self, sim_data):
        """Convert .sim file format to scenario format"""
        try:
            # Extract metadata and config
            metadata = sim_data.get('metadata', {})
            config = sim_data.get('config', {})
            
            # Create scenario format
            scenario_data = {
                'metadata': {
                    'name': metadata.get('mission_name', 'Converted Simulation'),
                    'mission_type': metadata.get('mission_type', 'search_and_destroy'),
                    'difficulty': 'Normal',
                    'time_limit': 300,
                    'map_width': config.get('map_width', 1080),
                    'map_height': config.get('map_height', 720),
                    'grid_size': config.get('grid_size', 20)
                },
                'items': []
            }
            
            # Convert drones
            for drone_data in sim_data.get('drones', []):
                scenario_data['items'].append({
                    'type': 'drone',
                    'position': drone_data.get('position', [100, 100]),
                    'properties': {
                        'drone_id': drone_data.get('drone_id', 0),
                        'max_missiles': drone_data.get('max_missiles', 2),
                        'formation_role': drone_data.get('formation_role', 'assault')
                    }
                })
            
            # Convert targets
            for target_data in sim_data.get('targets', []):
                scenario_data['items'].append({
                    'type': 'target',
                    'position': target_data.get('position', [500, 500]),
                    'properties': {
                        'target_type': target_data.get('target_type', 'standard'),
                        'health': target_data.get('health', 100),
                        'hidden': target_data.get('hidden', False)
                    }
                })
            
            # Convert obstacles - FIXED TO HANDLE DIFFERENT FORMATS
            for obs_data in sim_data.get('obstacles', []):
                try:
                    # Handle different obstacle data formats
                    if isinstance(obs_data, dict):
                        # Dictionary format with position and properties
                        pos = obs_data.get('position', [400, 300])
                        size = obs_data.get('size', 40)
                        width = obs_data.get('width', size)
                        height = obs_data.get('height', size)
                    elif isinstance(obs_data, (list, tuple)) and len(obs_data) >= 2:
                        # Array format [x, y] or [x, y, size]
                        pos = [obs_data[0], obs_data[1]]
                        size = obs_data[2] if len(obs_data) > 2 else 40
                        width = height = size
                    else:
                        # Unknown format - create default
                        pos = [400 + len(scenario_data['items']) * 60, 300]
                        width = height = 40
                    
                    scenario_data['items'].append({
                        'type': 'obstacle',
                        'position': pos,
                        'properties': {
                            'size': max(width, height),  # Use larger dimension
                            'width': int(width),
                            'height': int(height),
                            'destructible': False
                        }
                    })
                    print(f"Converted obstacle: pos={pos}, size={width}x{height}")
                    
                except Exception as e:
                    print(f"Error converting obstacle: {e}")
                    # Create a fallback obstacle
                    fallback_obs = {
                        'type': 'obstacle',
                        'position': [400 + len(scenario_data['items']) * 60, 300],
                        'properties': {
                            'size': 40,
                            'width': 40,
                            'height': 40,
                            'destructible': False
                        }
                    }
                    scenario_data['items'].append(fallback_obs)
            
            # Convert bases - FIXED TO HANDLE BOTH SINGLE AND ARRAY FORMATS
            bases_data = sim_data.get('bases', [])
            if bases_data:
                # Handle both single base object and array of bases
                if isinstance(bases_data, dict):
                    # Single base object
                    base_pos = bases_data.get('position', [50, 50])
                    capacity = bases_data.get('capacity', 10)
                elif isinstance(bases_data, list) and len(bases_data) > 0:
                    # Array of bases - use first one
                    first_base = bases_data[0]
                    base_pos = first_base.get('position', [50, 50])
                    capacity = first_base.get('capacity', 10)
                else:
                    # Fallback
                    base_pos = [50, 50]
                    capacity = 10
                
                scenario_data['items'].append({
                    'type': 'base',
                    'position': base_pos,
                    'properties': {
                        'capacity': capacity
                    }
                })
                print(f"Converted base: pos={base_pos}, capacity={capacity}")
            else:
                # No base data found - create default
                scenario_data['items'].append({
                    'type': 'base',
                    'position': [50, 50],
                    'properties': {
                        'capacity': 10
                    }
                })
                print("No base data found - created default base")
            
            return scenario_data
        
        except Exception as e:
            print(f"Error converting sim to scenario: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def parse_unknown_format(self, data):
        """Try to parse unknown file format"""
        scenario_data = {
            'metadata': {
                'name': 'Unknown Format Conversion',
                'mission_type': 'search_and_destroy',
                'difficulty': 'Normal',
                'time_limit': 300,
                'map_width': 1080,
                'map_height': 720,
                'grid_size': 20
            },
            'items': []
        }
        
        # Look for common keys and convert
        if 'drones' in data:
            for drone in data['drones']:
                scenario_data['items'].append({
                    'type': 'drone',
                    'position': drone.get('position', [100, 100]),
                    'properties': {
                        'drone_id': drone.get('drone_id', 0),
                        'max_missiles': drone.get('max_missiles', 2),
                        'formation_role': 'assault'
                    }
                })
        
        if 'targets' in data:
            for target in data['targets']:
                scenario_data['items'].append({
                    'type': 'target',
                    'position': target.get('position', [500, 500]),
                    'properties': {
                        'target_type': target.get('target_type', 'standard'),
                        'health': target.get('health', 100),
                        'hidden': target.get('hidden', False)
                    }
                })
        
        # Try different obstacle formats
        if 'obstacles' in data:
            print(f"Found obstacles in data: {data['obstacles']}")
            for i, obs in enumerate(data['obstacles']):
                print(f"Processing obstacle {i}: {obs}")
                
                # Handle different obstacle formats
                if isinstance(obs, dict):
                    # Dictionary format
                    pos = obs.get('position', [300 + i*60, 300])
                    size = obs.get('size', 40)
                elif isinstance(obs, list) and len(obs) >= 2:
                    # List format [x, y] or [x, y, size]
                    pos = [obs[0], obs[1]]
                    size = obs[2] if len(obs) > 2 else 40
                else:
                    # Unknown format - create default
                    pos = [300 + i*60, 300]
                    size = 40
                
                scenario_data['items'].append({
                    'type': 'obstacle',
                    'position': pos,
                    'properties': {
                        'size': size,
                        'destructible': False
                    }
                })
                print(f"Added obstacle at {pos} with size {size}")
        
        if 'bases' in data:
            for base in data['bases']:
                scenario_data['items'].append({
                    'type': 'base',
                    'position': base.get('position', [50, 50]),
                    'properties': {
                        'capacity': base.get('capacity', 10)
                    }
                })
        
        return scenario_data

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

    def debug_simulation_state(self):
        """Debug current simulation state"""
        print("=== SIMULATION DEBUG ===")
        print(f"Drones: {len(self.sim_manager.drones)}")
        for i, drone in enumerate(self.sim_manager.drones):
            print(f"  Drone {i}: pos={drone.position}, alive={getattr(drone, 'alive', True)}")
        
        print(f"Target: {self.sim_manager.target}")
        if self.sim_manager.target:
            print(f"  Target pos: {getattr(self.sim_manager.target, 'position', 'No position')}")
        
        print(f"Obstacles: {len(self.sim_manager.obstacles)}")
        for i, obs in enumerate(self.sim_manager.obstacles[:3]):  # First 3 only
            print(f"  Obstacle {i}: x={obs.x()}, y={obs.y()}, w={obs.width()}, h={obs.height()}")
        
        print(f"Base: {self.sim_manager.base}")
        print(f"Canvas size: {self.canvas.size()}")
        print(f"Canvas visible: {self.canvas.isVisible()}")
        print("========================")

    # Add this to MainWindow to test basic canvas drawing:

    def test_canvas_drawing(self):
        """Test if canvas can draw anything"""
        print("Testing canvas drawing...")
        
        # Force a simple drawing test
        def simple_paint(event):
            painter = QPainter(self.canvas)
            painter.fillRect(0, 0, 200, 200, QColor(255, 0, 0))  # Red square
            painter.drawText(50, 50, "TEST DRAWING")
            painter.end()
        
        # Temporarily override paintEvent
        original_paint = self.canvas.paintEvent
        self.canvas.paintEvent = simple_paint
        self.canvas.update()
        
        # Restore original
        QTimer.singleShot(2000, lambda: setattr(self.canvas, 'paintEvent', original_paint))

    def create_control_panel(self):
        """Create the control panel with buttons and settings"""
        panel = QWidget()
        layout = QHBoxLayout()
        panel.setLayout(layout)
        
        # Start/Pause button
        start_button = QPushButton("Start")
        start_button.setObjectName("start_button")
        start_button.clicked.connect(self.toggle_simulation)
        layout.addWidget(start_button)
        
        # Reset button
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_simulation)
        layout.addWidget(reset_button)
        
        # Grid toggle button
        grid_btn = QPushButton("Grid")
        grid_btn.setCheckable(True)
        grid_btn.clicked.connect(self.toggle_grid)
        layout.addWidget(grid_btn)
        
        # Paths toggle button
        paths_btn = QPushButton("Paths")
        paths_btn.setCheckable(True)
        paths_btn.clicked.connect(self.toggle_paths)
        layout.addWidget(paths_btn)
        
        # Debug toggle button
        debug_btn = QPushButton("Debug")
        debug_btn.setCheckable(True)
        debug_btn.clicked.connect(self.toggle_debug)
        layout.addWidget(debug_btn)
        
        # Performance toggle button
        perf_btn = QPushButton("Perf")
        perf_btn.setCheckable(True)
        perf_btn.clicked.connect(self.toggle_performance)
        layout.addWidget(perf_btn)
        
        # Stats toggle button
        stats_btn = QPushButton("Stats")
        stats_btn.setCheckable(True)
        stats_btn.clicked.connect(self.toggle_stats)
        layout.addWidget(stats_btn)
        
        # REMOVED: Radar button - radar is now always active
        
        # Editor button
        editor_btn = QPushButton("Editor")
        editor_btn.clicked.connect(self.open_scenario_editor)
        layout.addWidget(editor_btn)
        
        # Create dropdown for modes
        mode_dropdown = UIComponentManager.create_mode_dropdown(self.change_mode)
        layout.addWidget(mode_dropdown)
        
        # Create dropdown for radar speed (kept for controlling sweep speed)
        speed_dropdown = UIComponentManager.create_radar_speed_dropdown(self.change_radar_speed)
        layout.addWidget(speed_dropdown)
        
        # Store buttons reference without radar button
        self.buttons = {
            'start_button': start_button,
            'reset_button': reset_button,
            'grid_button': grid_btn,
            'paths_button': paths_btn,
            'debug_button': debug_btn,
            'perf_button': perf_btn,
            'stats_button': stats_btn,
            'editor_button': editor_btn,
            'mode_dropdown': mode_dropdown,
            'speed_dropdown': speed_dropdown
        }
        
        return panel

    def stop_simulation(self):
        """Stop the simulation"""
        self.simulation_running = False
        if self.timer.isActive():
            self.timer.stop()
        if hasattr(self, 'buttons') and 'start_button' in self.buttons:
            self.buttons['start_button'].setText("Start Simulation")

    def load_simulation_file(self, filename):
        """Load simulation from .sim file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Reset simulation first
            self.reset_simulation()
            
            # Load drones
            if 'drones' in data:
                for drone_data in data['drones']:
                    drone = Drone(
                        drone_id=drone_data['drone_id'],
                        x=drone_data['position'][0],
                        y=drone_data['position'][1]
                    )
                    drone.max_missiles = drone_data.get('max_missiles', 2)
                    drone.has_attacked = drone_data.get('has_attacked', False)
                    drone.alive = drone_data.get('alive', True)
                    
                    self.sim_manager.add_drone(drone)
            
            # Load targets
            if 'targets' in data:
                for target_data in data['targets']:
                    target = TargetFactory.create_target(
                        x=target_data['position'][0],
                        y=target_data['position'][1],
                        target_type=target_data.get('target_type', 'standard'),
                        health=target_data.get('health', 100)
                    )
                    target.hidden = target_data.get('hidden', False)
                    self.sim_manager.set_target(target)
            
            # Load obstacles - FIXED FOR .sim FILES
            if 'obstacles' in data:
                for obs_data in data['obstacles']:
                    try:
                        # Handle different obstacle data formats
                        if isinstance(obs_data, dict):
                            # New format with position and properties
                            pos = obs_data.get('position', [400, 300])
                            size = obs_data.get('size', 40)
                            width = obs_data.get('width', size)
                            height = obs_data.get('height', size)
                        else:
                            # Legacy format - assume it's position data
                            pos = obs_data if isinstance(obs_data, list) else [400, 300]
                            width = height = 40
                        
                        # Create obstacle using ObstacleFactory
                        obstacle = ObstacleFactory.create_standard_obstacle(
                            x=int(pos[0]),
                            y=int(pos[1]),
                            width=int(width),
                            height=int(height)
                        )
                        
                        self.sim_manager.add_obstacle(obstacle)
                        print(f"Loaded obstacle at ({pos[0]}, {pos[1]}) size {width}x{height}")
                        
                    except Exception as e:
                        print(f"Error loading obstacle: {e}")
                        # Create a fallback obstacle
                        fallback_obs = ObstacleFactory.create_standard_obstacle(
                            x=400 + len(self.sim_manager.obstacles) * 60,
                            y=300,
                            width=40,
                            height=40
                        )
                        self.sim_manager.add_obstacle(fallback_obs)
            
            # Load bases
            if 'bases' in data:
                for base_data in data['bases']:
                    base_pos = base_data['position']
                    base = QRect(base_pos[0], base_pos[1], 40, 40)  # Standard base size
                    self.sim_manager.set_base(base)
            
            # Load configuration
            if 'config' in data:
                config = data['config']
                mode_name = config.get('mode', 'normal')
                
                # Map mode names to enum values
                mode_mapping = {
                    'normal': Modes.NORMAL,
                    'search_and_destroy': Modes.SEARCH_AND_DESTROY,
                    'escort': Modes.ESCORT,
                    'reconnaissance': Modes.RECONNAISSANCE,
                    'defensive': Modes.DEFENSIVE,
                    'bombing_run': Modes.BOMBING_RUN,
                    'patrol': Modes.PATROL,
                    'search_and_rescue': Modes.SEARCH_AND_RESCUE
                }
                
                mode = mode_mapping.get(mode_name, Modes.NORMAL)
                if self.sim_modes:
                    self.sim_modes.set_mode(mode)
                    
                    # Configure drones and targets for the mode
                    handler = self.sim_modes.get_current_handler()
                    if self.sim_manager.drones:
                        handler.configure_drones(self.sim_manager.drones)
                    if self.sim_manager.target:
                        handler.configure_target(self.sim_manager.target)
            
            # Update movement controller with new simulation data
            self._init_simulation()
            
            # Update UI
            self.canvas.update_simulation_data(
                self.sim_manager,
                self.movement_controller,
                self.renderer,
                self.missile_renderer,
                self.radar_renderer
            )
            
            print(f"Loaded simulation: {len(self.sim_manager.drones)} drones, {len(self.sim_manager.obstacles)} obstacles")
            self.canvas.update()
            
            return True
            
        except Exception as e:
            print(f"Error loading simulation file: {e}")
            QMessageBox.warning(self, "Load Error", f"Failed to load simulation file:\n{str(e)}")
            return False


