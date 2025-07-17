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
        """Initialize all components"""
        # Core components
        self.sim_manager = SimulationManager()
        self.sim_modes = SimModes()
        self.sim_modes.set_mode(Modes.NORMAL)
        
        # Rendering components
        self.renderer = Renderer()
        self.renderer.sim_modes = self.sim_modes
        self.missile_renderer = MissileRenderer()
        self.radar_renderer = RadarRenderer()
        self.explosion_manager = ExplosionManager()
        self.screen_flash = ScreenFlash()
        
        # UI panels - Make sure they get the main window as parent
        self.debug_panel = DebugPanel(self)
        self.performance_panel = PerformancePanel(self)
        self.statistics_panel = StatisticsPanel(self)
        self.alert_system = AlertSystem(self)
        self.status_checker = StatusChecker()
        
        self.panel_controller = PanelController(self)
        
        # Simulation controller
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
            'toggle_radar': self.toggle_radar,
            'change_mode': self.change_mode,
            'change_radar_speed': self.change_radar_speed,
            'launch_scenario_editor': self.launch_scenario_editor
        }

    def _init_simulation(self):
        """Initialize simulation using manager"""
        # Initialize empty simulation
        self.sim_manager.drones.clear()
        self.sim_manager.obstacles.clear()
        
        # Initialize base with default position - FIX THE NONE BASE ISSUE
        from PyQt5.QtCore import QRect
        from Config.SimulationConfig import SimulationConfig
        
        # Create default base if it doesn't exist
        if self.sim_manager.base is None:
            self.sim_manager.base = QRect(50, 50, SimulationConfig.BASE_SIZE, SimulationConfig.BASE_SIZE)
        
        # Create a placeholder target instead of None
        try:
            from EnemySystem.Target import Target
            # Create an invisible placeholder target that won't be rendered
            placeholder_target = Target(0, 0)
            placeholder_target.hidden = True
            placeholder_target.is_placeholder = True
            self.sim_manager.target = placeholder_target
        except Exception as e:
            print(f"Could not create placeholder target: {e}")
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
        
        print("Initialized empty simulation - load a scenario to begin")

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
        self.show_grid = not self.show_grid
        UIComponentManager.update_button_style(self.buttons['grid_button'], self.show_grid, 'grid_button')

    def toggle_paths(self):
        self.show_paths = not self.show_paths
        UIComponentManager.update_button_style(self.buttons['path_button'], self.show_paths, 'path_button')

    def toggle_debug(self):
        self.show_debug = not self.show_debug
        UIComponentManager.update_button_style(self.buttons['debug_button'], self.show_debug, 'debug_button')
        
        if self.show_debug:
            self.debug_panel.create_panel()
        else:
            self.debug_panel.hide_panel()

    def toggle_radar(self):
        radar_enabled = self.radar_renderer.toggle_radar()
        UIComponentManager.update_button_style(self.buttons['radar_button'], radar_enabled, 'radar_button')

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
            
            # Ensure base exists - DON'T RESET BASE TO NONE
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
            
            print("Simulation reset successfully")
            
        except Exception as e:
            print(f"Error in reset_simulation: {e}")

    def change_mode(self, mode_text):
        for mode in Modes:
            if mode.value == mode_text:
                self.sim_modes.set_mode(mode)
                # Recreate movement controller with new mode
                self.movement_controller = MainController(
                    self.sim_manager.drones,
                    self.sim_manager.obstacles,
                    self.sim_manager.target,
                    self.sim_manager.base,
                    self.sim_modes,
                    alert_system=self.alert_system  # <-- ADD THIS LINE
                )
                self.sim_manager.movement_controller = self.movement_controller
                # Apply mode rules to drones and target
                self.sim_modes.apply_mode_to_simulation(self.sim_manager.drones, self.sim_manager.target)
                # Update missile status labels
                for label in self.missile_status_labels:
                    label.deleteLater()
                self.missile_status_labels = UIComponentManager.create_missile_status_labels(
                    self.sim_manager.drones, self.missile_status_layout
                )

                # --- Mode-specific UI and logic ---
                handler = self.sim_modes.get_current_handler()
                # Radar logic - UPDATED WITH ESCORT
                radar_modes = {
                    "normal_mode": (False, "normal"),
                    "search_and_destroy": (True, "fast"),
                    "escort": (True, "normal"),  # Fixed: escort mode uses radar for threat detection
                    "reconnaissance": (True, "slow"),
                    "defensive": (True, "normal"),
                    "bombing_run": (True, "fast"),
                    "patrol": (True, "normal"),
                    "search_and_rescue": (True, "fast"),
                }
                mode_key = getattr(handler, "mode_name", mode.value)
                radar_enabled, sweep_speed = radar_modes.get(mode_key, (False, "normal"))
                self.radar_renderer.enable_radar(radar_enabled)
                UIComponentManager.update_button_style(self.buttons['radar_button'], radar_enabled, 'radar_button')
                self.radar_renderer.set_sweep_speed(sweep_speed)

                # Target visibility logic
                # This is handled in Renderer.draw_static_elements using should_show_target and spotted_by_radar
                # But you may want to force update here if needed

                self._update_panels()
                break

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
        print(f"Radar speed changed to: {speed_text}")

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
                print("Created default base for scenario loading")
        
            # Reset simulation first
            self.reset_simulation()
            
            # Apply mission settings with error handling
            metadata = scenario_data.get('metadata', {})
            mission_type = metadata.get('mission_type', 'normal').lower()
            
            # Count drones in scenario to determine drone count
            items = scenario_data.get('items', [])
            scenario_drones = [item for item in items if item.get('type') == 'drone']
            num_drones_in_scenario = len(scenario_drones)
            
            print(f"Scenario has {num_drones_in_scenario} drones")
            
            # Safe mode setting with fallback
            try:
                if mission_type == 'search_and_destroy' and hasattr(Modes, 'SEARCH_AND_DESTROY'):
                    self.sim_modes.set_mode(Modes.SEARCH_AND_DESTROY)
                elif mission_type == 'escort' and hasattr(Modes, 'ESCORT'):
                    self.sim_modes.set_mode(Modes.ESCORT)
                else:
                    self.sim_modes.set_mode(Modes.NORMAL)
            except Exception as e:
                print(f"Mode setting error: {e}")
                self.sim_modes.set_mode(Modes.NORMAL)
            
            # Clear existing elements
            self.sim_manager.drones.clear()
            self.sim_manager.obstacles.clear()
            
            # Process items with proper drone ID tracking
            drone_count = 0
            for item in items:
                try:
                    item_type = item.get('type')
                    
                    # Fix: Ensure position is always a list/array
                    position = item.get('position', [100, 100])
                    if isinstance(position, (int, float)):
                        position = [position, position]
                    elif not isinstance(position, (list, tuple)):
                        position = [100, 100]
                    
                    if len(position) < 2:
                        position = position + [100] * (2 - len(position))
                    
                    properties = item.get('properties', {})
                    
                    if item_type == 'drone':
                        # Create drone with sequential ID
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
                        print(f"Created drone {drone_count-1} at position {position}")
                        
                    elif item_type == 'target':
                        # Create target with error handling - FIXED TARGET POSITION
                        try:
                            from EnemySystem.Target import Target
                            
                            # Ensure position is [x, y] format
                            target_x = float(position[0])
                            target_y = float(position[1])
                            
                            target = Target(target_x, target_y)
                            
                            # CRITICAL FIX: Ensure position is stored as numpy array with correct format
                            import numpy as np
                            target.position = np.array([target_x, target_y], dtype=float)
                            
                            print(f"Created target at position {target.position} (type: {type(target.position)})")
                            
                        except ImportError:
                            from EnemySystem.Target import target as Target
                            target_x = float(position[0])
                            target_y = float(position[1])
                            target = Target(target_x, target_y)
                            
                            # CRITICAL FIX: Ensure position is stored as numpy array with correct format
                            import numpy as np
                            target.position = np.array([target_x, target_y], dtype=float)
                            
                            print(f"Created target at position {target.position} (type: {type(target.position)})")
                        
                        # Set target properties safely
                        if hasattr(target, 'health'):
                            target.health = properties.get('health', 100)
                        if hasattr(target, 'hidden'):
                            target.hidden = properties.get('hidden', False)
                        
                        # Mark as VIP for escort missions
                        if mission_type == 'escort':
                            target.is_vip = True
                            target.needs_escort = True
                        
                        self.sim_manager.target = target
                        print(f"Created target at position [{target_x}, {target_y}]")
                        
                    elif item_type == 'obstacle':
                        # Create obstacle with error handling
                        try:
                            from Factory.ObstacleFactory import ObstacleFactory
                            obstacle = ObstacleFactory.create_obstacle(
                                float(position[0]), float(position[1]), 
                                properties.get('size', 40)
                            )
                            self.sim_manager.obstacles.append(obstacle)
                            print(f"Created obstacle at position {position}")
                        except Exception as e:
                            print(f"Error creating obstacle: {e}")
                            
                    elif item_type == 'base':
                        # Update base position with error handling - FIX TYPE CONVERSION
                        try:
                            base_x = int(float(position[0]))
                            base_y = int(float(position[1]))
                            base_size = properties.get('size', SimulationConfig.BASE_SIZE)
                            
                            # Update base position and size
                            self.sim_manager.base.setX(base_x)
                            self.sim_manager.base.setY(base_y)
                            self.sim_manager.base.setWidth(base_size)
                            self.sim_manager.base.setHeight(base_size)
                            
                            print(f"Set base position to [{base_x}, {base_y}] with size {base_size}")
                        except Exception as e:
                            print(f"Error setting base position: {e}")
                
                except Exception as e:
                    print(f"Error processing item {item}: {e}")
                    continue
    
            # Reinitialize movement controller with the actual number of drones created
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
                print(f"Reinitialized movement controller with {len(self.sim_manager.drones)} drones")
            except Exception as e:
                print(f"Error creating movement controller: {e}")
            
            # Clear and recreate missile status labels for actual drone count
            try:
                for label in self.missile_status_labels:
                    label.deleteLater()
                self.missile_status_labels = UIComponentManager.create_missile_status_labels(
                    self.sim_manager.drones, self.missile_status_layout
                )
                print(f"Created missile status labels for {len(self.sim_manager.drones)} drones")
            except Exception as e:
                print(f"Error updating missile status labels: {e}")
            
            # Update canvas with simulation data - ENHANCED DEBUGGING
            try:
                print("Updating canvas with simulation data...")
                
                # Connect canvas to simulation data
                self.canvas.sim_manager = self.sim_manager
                self.canvas.movement_controller = self.movement_controller
                self.canvas.renderer = self.renderer
                self.canvas.missile_renderer = self.missile_renderer
                self.canvas.radar_renderer = self.radar_renderer
                self.canvas.explosion_manager = self.explosion_manager
                self.canvas.screen_flash = self.screen_flash
                
                print(f"Canvas sim_manager: {self.canvas.sim_manager}")
                print(f"Canvas renderer: {self.canvas.renderer}")
                print(f"Canvas drones: {len(self.canvas.sim_manager.drones) if self.canvas.sim_manager else 'None'}")
                
                # Set canvas properties to match main window
                self.canvas.show_grid = self.show_grid
                self.canvas.show_paths = self.show_paths
                self.canvas.show_debug = self.show_debug
                
                print(f"Canvas show_grid: {self.canvas.show_grid}")
                print(f"Canvas show_debug: {self.canvas.show_debug}")
                
                # Force multiple updates
                self.canvas.update()
                self.canvas.repaint()
                QApplication.processEvents()  # Process any pending events
                
                # Try to trigger a paint event manually
                paint_event = QPaintEvent(self.canvas.rect())
                QApplication.sendEvent(self.canvas, paint_event)
                
                print(f"Canvas updated with simulation data")
            except Exception as e:
                print(f"Error updating canvas: {e}")
                import traceback
                traceback.print_exc()
        
        except Exception as e:
            print(f"Error in apply_scenario_to_simulation: {e}")
            QMessageBox.critical(self, "Error", f"Failed to apply scenario: {str(e)}")

        # Call debug to see what we have
        self.debug_simulation_state()

        # Force canvas to show elements immediately
        try:
            # Force canvas geometry update
            self.canvas.setMinimumSize(800, 600)
            self.canvas.resize(1080, 720)
            
            # Multiple update attempts
            for i in range(3):
                self.canvas.update()
                self.canvas.repaint()
                QApplication.processEvents()
                
            print("Forced canvas updates completed")
            
        except Exception as e:
            print(f"Error in forced canvas update: {e}")

        print(f"Scenario loaded successfully: {len(self.sim_manager.drones)} drones, "
              f"{len(self.sim_manager.obstacles)} obstacles")

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
                
                # Check format and convert if needed
                if 'metadata' in data and 'drones' in data and 'config' in data:
                    # It's a .sim file - convert to scenario format
                    scenario_data = self.convert_sim_to_scenario(data)
                else:
                    # It's already scenario format
                    scenario_data = data
                
                # Apply the scenario to simulation
                self.apply_scenario_to_simulation(scenario_data)
                
                QMessageBox.information(self, "Success", f"Simulation loaded: {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load simulation: {str(e)}")

    def convert_sim_to_scenario(self, sim_data):
        """Convert .sim format to .scenario format"""
        scenario_data = {
            'metadata': {
                'name': sim_data['metadata'].get('mission_name', 'Converted Scenario'),
                'mission_type': sim_data['metadata'].get('mission_type', 'search_and_destroy'),
                'difficulty': 'Normal',
                'time_limit': 300,
                'map_width': sim_data['config'].get('map_width', 1080),
                'map_height': sim_data['config'].get('map_height', 720),
                'grid_size': sim_data['config'].get('grid_size', 20)
            },
            'items': []
        }
        
        # Convert drones
        for drone in sim_data.get('drones', []):
            scenario_data['items'].append({
                'type': 'drone',
                'position': drone['position'],
                'properties': {
                    'drone_id': drone['drone_id'],
                    'max_missiles': drone.get('max_missiles', 2),
                    'formation_role': drone.get('formation_role', 'assault')
                }
            })
        
        # Convert targets
        for target in sim_data.get('targets', []):
            scenario_data['items'].append({
                'type': 'target',
                'position': target['position'],
                'properties': {
                    'target_type': target.get('target_type', 'standard'),
                    'health': target.get('health', 100),
                    'hidden': target.get('hidden', False)
                }
            })
        
        # Convert obstacles
        for obstacle in sim_data.get('obstacles', []):
            scenario_data['items'].append({
                'type': 'obstacle',
                'position': obstacle['position'],
                'properties': {
                    'size': obstacle.get('size', 40),
                    'destructible': obstacle.get('destructible', False)
                }
            })
        
        # Convert bases
        for base in sim_data.get('bases', []):
            scenario_data['items'].append({
                'type': 'base',
                'position': base['position'],
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
