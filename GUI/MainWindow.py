import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMainWindow
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

from GUI.UIComponentManager import UIComponentManager
from GUI.SimulationManager import SimulationManager
from GUI.DebugPanel import DebugPanel
from GUI.StatusChecker import StatusChecker
from GUI.Renderer import Renderer
from GUI.PerformancePanel import PerformancePanel
from GUI.StatisticsPanel import StatisticsPanel
from GUI.AlertSystem import AlertSystem
from GUI.MissileRenderer import MissileRenderer
from GUI.RadarRenderer import RadarRenderer
from GUI.ExplosionEffects import ExplosionManager, ScreenFlash
from DroneSystem.SimulationController import SimulationController
from DroneSystem.DroneStateManager import DroneStateManager
from DroneSystem.MainController import MainController
from Config.SimulationConfig import SimulationConfig
from SimMode.Modes import SimModes, Modes
from Factory.TargetFactory import TargetFactory
from Utils.SaveLoadManager import SaveLoadManager

class SimulationCanvas(QWidget):
    """Custom widget for drawing the simulation"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setMinimumSize(800, 600)
        
    def paintEvent(self, event):
        """Paint the simulation"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate offset for control panel
        offset_y = SimulationConfig.CONTROL_PANEL_HEIGHT + 15
        
        try:
            # Draw background first
            painter.fillRect(self.rect(), Qt.white)
            
            # Draw grid if enabled
            if self.main_window.show_grid:
                self.main_window.renderer.draw_grid(painter, offset_y, self.main_window.sim_manager.movement_controller)
            
            # Draw static elements (obstacles, target, base)
            self.main_window.renderer.draw_static_elements(
                painter, offset_y, self.main_window.sim_manager.obstacles, 
                self.main_window.sim_manager.target, self.main_window.sim_manager.base
            )
            
            # Draw radar
            self.main_window.radar_renderer.draw_radar(painter, self.main_window.sim_manager.drones, self.main_window.sim_manager.obstacles, offset_y)
            
            # Draw drones
            for drone in self.main_window.sim_manager.drones:
                if drone.alive:  # Only draw active drones
                    self.main_window.renderer.draw_drone_with_status(painter, drone, offset_y, SimulationConfig.DRONE_SIZE)
            
            # Draw paths if enabled
            if self.main_window.show_paths:
                self.main_window.renderer.draw_paths(painter, offset_y, self.main_window.sim_manager.drones)
            
            # Draw missiles
            if hasattr(self.main_window.sim_manager.movement_controller, 'missile_manager'):
                self.main_window.missile_renderer.draw_missiles(painter, self.main_window.sim_manager.movement_controller.missile_manager, offset_y)
            
            # Draw explosion effects
            self.main_window.explosion_manager.draw_all(painter, SimulationConfig.CONTROL_PANEL_HEIGHT)
            self.main_window.screen_flash.draw(painter, self.width(), self.height())
            
        except Exception as e:
            print(f"Error in paintEvent: {e}")
            # Draw error message
            painter.setPen(Qt.red)
            painter.drawText(50, 100, f"Rendering Error: {str(e)}")
        
        painter.end()

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
        
        # UI panels
        self.debug_panel = DebugPanel(self)
        self.performance_panel = PerformancePanel(self)
        self.statistics_panel = StatisticsPanel(self)
        self.alert_system = AlertSystem(self)
        self.status_checker = StatusChecker()
        
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
            from PyQt5.QtWidgets import QPushButton
            test_button = QPushButton("Test Button")
            main_layout.addWidget(test_button)
        
        # Add the simulation canvas
        self.simulation_canvas = SimulationCanvas(self)
        main_layout.addWidget(self.simulation_canvas)

        # Bottom status area
        bottom_layout = QHBoxLayout()
        self.missile_status_layout = QVBoxLayout()
        self.missile_status_layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        
        bottom_layout.addLayout(self.missile_status_layout)
        bottom_layout.addStretch()
        
        main_layout.addLayout(bottom_layout)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

    def _get_ui_callbacks(self):
        """Get all UI callback functions"""
        return {
            'toggle_simulation': self.toggle_simulation,
            'reset_simulation': self.reset_simulation,
            'toggle_grid': self.toggle_grid,
            'toggle_paths': self.toggle_paths,
            'toggle_debug': self.toggle_debug,
            'toggle_statistics': self.toggle_statistics,
            'toggle_performance': self.toggle_performance,
            'toggle_radar': self.toggle_radar,
            'change_mode': self.change_mode,
            'change_radar_speed': self.change_radar_speed
        }

    def _init_simulation(self):
        """Initialize simulation using manager"""
        self.sim_manager.init_default_simulation()
        self.movement_controller = MainController(
            self.sim_manager.drones, 
            self.sim_manager.obstacles, 
            self.sim_manager.target, 
            self.sim_manager.base,
            self.sim_modes
        )
        self.sim_manager.movement_controller = self.movement_controller
        
        # Create missile status labels
        self.missile_status_labels = UIComponentManager.create_missile_status_labels(
            self.sim_manager.drones, self.missile_status_layout
        )

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
            self.alert_system.show_drone_destroyed_alert(drone.drone_id)
            drone._destruction_alerted = True
        
        if drone.missiles_fired >= drone.max_missiles and not hasattr(drone, '_missiles_alerted'):
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

    def toggle_performance(self):
        if self.performance_panel.is_visible:
            self.performance_panel.hide_panel()
            UIComponentManager.update_button_style(self.buttons['perf_button'], False, 'perf_button')
        else:
            self.performance_panel.show_panel()
            UIComponentManager.update_button_style(self.buttons['perf_button'], True, 'perf_button')
        # Force update panel after toggling
        self.performance_panel.update_metrics(self.sim_manager.drones, self.sim_manager.movement_controller)

    def toggle_statistics(self):
        if self.statistics_panel.is_visible:
            self.statistics_panel.hide_panel()
            UIComponentManager.update_button_style(self.buttons['stats_button'], False, 'stats_button')
        else:
            self.statistics_panel.show_panel()
            UIComponentManager.update_button_style(self.buttons['stats_button'], True, 'stats_button')
        # Force update panel after toggling
        self.statistics_panel.update_statistics(self.sim_manager.drones, self.sim_manager.movement_controller)

    def reset_simulation(self):
        # Clear existing labels
        for label in self.missile_status_labels:
            label.deleteLater()
        
        # Reset simulation
        self.simulation_controller.reset_simulation()
        
        # Recreate target and controller
        self.sim_manager.target = TargetFactory.create_random_target(self.sim_manager.obstacles)
        self.movement_controller = MainController(
            self.sim_manager.drones, self.sim_manager.obstacles, 
            self.sim_manager.target, self.sim_manager.base,
            self.sim_modes
        )
        self.sim_manager.movement_controller = self.movement_controller
        
        # Recreate labels
        self.missile_status_labels = UIComponentManager.create_missile_status_labels(
            self.sim_manager.drones, self.missile_status_layout
        )

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
                    self.sim_modes
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
                # Radar logic
                radar_modes = {
                    "normal_mode": (False, "normal"),
                    "search_and_destroy": (True, "fast"),
                    "escort": (False, "normal"),
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
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        
        # Save action
        save_action = file_menu.addAction('Save Simulation')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_load_manager.save_simulation)
        
        # Load action
        load_action = file_menu.addAction('Load Simulation')
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.save_load_manager.load_simulation)
        
        file_menu.addSeparator()
        
        # Quick save/load
        quick_save_action = file_menu.addAction('Quick Save')
        quick_save_action.setShortcut('F5')
        quick_save_action.triggered.connect(self.quick_save)
        
        quick_load_action = file_menu.addAction('Quick Load')
        quick_load_action.setShortcut('F9')
        quick_load_action.triggered.connect(self.quick_load)
        
    def quick_save(self):
        self.save_load_manager.save_simulation('quicksave.sim')
        
    def quick_load(self):
        self.save_load_manager.load_simulation('quicksave.sim')
        # Reinitialize controllers and UI after loading
        self.movement_controller = MainController(
            self.sim_manager.drones, self.sim_manager.obstacles,
            self.sim_manager.target, self.sim_manager.base, self.sim_modes
        )
        self.sim_manager.movement_controller = self.movement_controller
        # Update missile status labels
        for label in self.missile_status_labels:
            label.deleteLater()
        self.missile_status_labels = UIComponentManager.create_missile_status_labels(
            self.sim_manager.drones, self.missile_status_layout
        )
        self._update_panels()

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
            self.sim_manager.targets, self.sim_manager.base, self.sim_modes
        )
        self.sim_manager.movement_controller = self.movement_controller
