import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

from core.simulation.SimulationManager import SimulationManager
from gui.panels.DebugPanel import DebugPanel
from gui.StatusChecker import StatusChecker
from gui.rendering.Renderer import Renderer
from gui.rendering.ConcreteRenderer import ConcreteRenderer
from gui.panels.PerformancePanel import PerformancePanel
from gui.panels.StatisticsPanel import StatisticsPanel
from gui.Components.AlertSystem import AlertSystem
from gui.rendering.MissileRenderer import MissileRenderer
from gui.rendering.RadarRenderer import RadarRenderer
from gui.effects.ExplosionEffects import ExplosionManager, ScreenFlash
from core.simulation.SimulationController import SimulationController
from drone_system.ai.DroneStateManager import DroneStateManager
from core.simulation.SimulationController import MainController
from config.SimulationConfig import SimulationConfig
from simulation_modes.ModeManager import ModeManager
from simulation_modes.ModeTypes import Modes
from core.entities.targets.TargetFactory import TargetFactory
from utils.io.SaveLoadManager import SaveLoadManager

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
            painter.fillRect(self.rect(), QColor(255, 255, 255))
            
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
            

            # Draw drones (simple and safe)
            drones = getattr(self.main_window.sim_manager, 'drones', [])
            
            for i, drone in enumerate(drones):
                try:
                    # Safe attribute access with defaults
                    x = getattr(drone, 'x', 100 + i * 50)
                    y = getattr(drone, 'y', 100 + i * 30)
                    alive = getattr(drone, 'alive', True)
                    drone_id = getattr(drone, 'drone_id', i + 1)
                    
                    if alive:
                        # Draw drone as blue circle
                        painter.setPen(QPen(QColor(100, 150, 255), 2))
                        painter.setBrush(QBrush(QColor(100, 150, 255)))
                        drone_size = 15
                        painter.drawEllipse(
                            int(x - drone_size/2), 
                            int(y + offset_y - drone_size/2), 
                            drone_size, 
                            drone_size
                        )
                        
                        # Draw drone ID
                        painter.setPen(QPen(QColor(255, 255, 255)))
                        painter.drawText(int(x - 5), int(y + offset_y + 5), str(drone_id))
                        
                except Exception as drone_error:
                    # Fallback: draw a simple drone at default position
                    painter.setPen(QPen(QColor(100, 150, 255), 2))
                    painter.setBrush(QBrush(QColor(100, 150, 255)))
                    default_x = 100 + i * 50
                    default_y = 150 + i * 30
                    painter.drawEllipse(
                        int(default_x - 7), 
                        int(default_y + offset_y - 7), 
                        14, 14
                    )
                    painter.setPen(QPen(QColor(255, 255, 255)))
                    painter.drawText(int(default_x - 3), int(default_y + offset_y + 3), str(i+1))
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
            painter.setPen(QColor(255, 120, 120))
            painter.drawText(50, 100, f"Rendering Error: {str(e)}")
        
        painter.end()

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 700)
        super().__init__()
        self._init_window()
        self._init_components()
        self._init_ui()
        self._init_simulation()
        self.save_load_manager = SaveLoadManager()
        self.create_file_menu()

    def _init_window(self):
        """Initialize window properties"""
        self.setWindowTitle("Drone Simulator")
        self.resize(SimulationConfig.WINDOW_WIDTH, SimulationConfig.WINDOW_HEIGHT)
        self.setStyleSheet("background-color: #f8f8f8;")

    def _init_components(self):
        """Initialize all components"""
        # Core components
        self.sim_manager = SimulationManager()
        self.sim_modes = ModeManager()
        self.sim_modes.set_mode(Modes.NORMAL)
        
        # Rendering components
        self.renderer = ConcreteRenderer()  # This needs a concrete implementation
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
        self.simulation_controller = SimulationController()
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


    
    def create_callback_handlers(self):
        """Create callback handlers for UI components"""
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

    def _init_ui(self):
        """Initialize the user interface with proper control panel layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create control panel with all buttons
        control_panel = QWidget()
        control_panel.setFixedHeight(SimulationConfig.CONTROL_PANEL_HEIGHT)
        control_panel.setStyleSheet("background-color: #f5f5f5; border-bottom: 1px solid #ccc;")
        
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create callback handlers first
        callbacks = self.create_callback_handlers()
        
        # Start Simulation button
        start_button = QPushButton("Start Simulation")
        start_button.setStyleSheet("background-color: #A8E6A8; padding: 10px 18px; border-radius: 5px; border: 1px solid #ddd; font-weight: bold; font-size: 14px;")
        start_button.clicked.connect(callbacks['toggle_simulation'])
        control_layout.addWidget(start_button)
        
        # Reset button
        reset_button = QPushButton("Reset")
        reset_button.setStyleSheet("background-color: #FFB3B3; padding: 10px 18px; border-radius: 5px; border: 1px solid #ddd;")
        reset_button.clicked.connect(callbacks['reset_simulation'])
        control_layout.addWidget(reset_button)
        
        # Grid button
        grid_button = QPushButton("Grid")
        grid_button.setStyleSheet("background-color: #D4E8FF; padding: 10px 18px; border-radius: 5px; border: 1px solid #ddd;")
        grid_button.clicked.connect(callbacks['toggle_grid'])
        control_layout.addWidget(grid_button)
        
        # Paths button
        paths_button = QPushButton("Paths")
        paths_button.setStyleSheet("background-color: #D4E8FF; padding: 10px 18px; border-radius: 5px; border: 1px solid #ddd;")
        paths_button.clicked.connect(callbacks['toggle_paths'])
        control_layout.addWidget(paths_button)
        
        # Debug button
        debug_button = QPushButton("Debug")
        debug_button.setStyleSheet("background-color: #D4E8FF; padding: 10px 18px; border-radius: 5px; border: 1px solid #ddd;")
        debug_button.clicked.connect(callbacks['toggle_debug'])
        control_layout.addWidget(debug_button)
        
        # Stats button
        stats_button = QPushButton("Stats")
        stats_button.setStyleSheet("background-color: #D4E8FF; padding: 10px 18px; border-radius: 5px; border: 1px solid #ddd;")
        stats_button.clicked.connect(callbacks['toggle_statistics'])
        control_layout.addWidget(stats_button)
        
        # Perf button
        perf_button = QPushButton("Perf")
        perf_button.setStyleSheet("background-color: #D4E8FF; padding: 10px 18px; border-radius: 5px; border: 1px solid #ddd;")
        perf_button.clicked.connect(callbacks['toggle_performance'])
        control_layout.addWidget(perf_button)
        
        # Radar button
        radar_button = QPushButton("Radar")
        radar_button.setStyleSheet("background-color: #D4E8FF; padding: 10px 18px; border-radius: 5px; border: 1px solid #ddd;")
        radar_button.clicked.connect(callbacks['toggle_radar'])
        control_layout.addWidget(radar_button)
        
        # Mode dropdown
        # QLabel and QComboBox already imported at top, QPushButton, QLabel, QComboBox
        control_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Normal", "Recon", "Search Destroy"])
        self.mode_combo.setCurrentText("Normal")
        self.mode_combo.currentTextChanged.connect(callbacks['change_mode'])
        control_layout.addWidget(self.mode_combo)
        
        # Radar Speed dropdown
        control_layout.addWidget(QLabel("Radar Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["Slow", "Normal", "Fast", "Very Fast", "Ultra Fast"])
        self.speed_combo.setCurrentText("Normal")
        self.speed_combo.currentTextChanged.connect(callbacks['change_radar_speed'])
        control_layout.addWidget(self.speed_combo)
        
        # Store buttons for later reference
        self.buttons = {
            'start_button': start_button,
            'reset_button': reset_button,
            'grid_button': grid_button,
            'paths_button': paths_button,
            'debug_button': debug_button,
            'stats_button': stats_button,
            'perf_button': perf_button,
            'radar_button': radar_button
        }
        
        # Add control panel to main layout
        main_layout.addWidget(control_panel)
        
        # Create simulation canvas
        self.simulation_canvas = SimulationCanvas(self)
        main_layout.addWidget(self.simulation_canvas)
        
        # Create status area for missile labels at bottom
        status_widget = QWidget()
        status_widget.setFixedHeight(40)
        status_widget.setStyleSheet("background-color: #f8f8f8; border-top: 1px solid #ccc;")
        
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        # Create missile status labels
        try:
            drones = getattr(self.sim_manager, 'drones', [])
            self.missile_status_labels = []
            
            for i, drone in enumerate(drones):
                drone_id = getattr(drone, 'drone_id', i+1)
                missiles_fired = getattr(drone, 'missiles_fired', 0)
                max_missiles = getattr(drone, 'max_missiles', 2)
                alive = getattr(drone, 'alive', True)
                
                status_text = f"Drone {drone_id}: {missiles_fired}/{max_missiles} missiles - {'Alive' if alive else 'Destroyed'}"
                label = QLabel(status_text)
                label.setStyleSheet("color: green; font-size: 12px; background-color: rgba(255,255,255,150); padding: 2px 5px; border-radius: 3px; margin-right: 10px;")
                status_layout.addWidget(label)
                self.missile_status_labels.append(label)
                
        except Exception as e:
            print(f"Error creating missile status: {e}")
            self.missile_status_labels = []
        
        # Add status widget to main layout
        main_layout.addWidget(status_widget)
        
        print("✅ UI initialized with proper control panel layout")
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
            self.sim_manager, 
            self.radar_renderer, 
            self.status_checker,
            self.explosion_manager, 
            self.screen_flash
        )
        self.sim_manager.movement_controller = self.movement_controller
        
        # Create missile status labels
        # # self.missile_status_labels = UIComponentManager.create_missile_status_labels( # Removed UIComponentManager dependency # Removed UIComponentManager dependency
        # self.sim_manager.drones, self.missile_status_layout # Fixed indentation and commented out)

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
        if not getattr(drone, "alive", True) and not hasattr(drone, '_destruction_alerted'):
            self.alert_system.show_drone_destroyed_alert(getattr(drone, "drone_id", "?"))
            drone._destruction_alerted = True
        
        if drone.missiles_fired >= getattr(drone, "max_missiles", 2) and not hasattr(drone, '_missiles_alerted'):
            self.alert_system.show_all_missiles_fired_alert(getattr(drone, "drone_id", "?"))
            drone._missiles_alerted = True
        
        if hasattr(drone, 'has_landed') and drone.has_landed and not hasattr(drone, '_landing_alerted'):
            self.alert_system.show_drone_landed_alert(getattr(drone, "drone_id", "?"))
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
        # UIComponentManager.update_button_style(self.buttons['grid_button'], self.show_grid, 'grid_button') # Removed UIComponentManager dependency

    def toggle_paths(self):
        self.show_paths = not self.show_paths
        # UIComponentManager.update_button_style(self.buttons['path_button'], self.show_paths, 'path_button') # Removed UIComponentManager dependency

    def toggle_debug(self):
        self.show_debug = not self.show_debug
        # UIComponentManager.update_button_style(self.buttons['debug_button'], self.show_debug, 'debug_button') # Removed UIComponentManager dependency
        
        if self.show_debug:
            self.debug_panel.create_panel()
        else:
            self.debug_panel.hide_panel()

    def toggle_radar(self):
        radar_enabled = self.radar_renderer.toggle_radar()
        # UIComponentManager.update_button_style(self.buttons['radar_button'], radar_enabled, 'radar_button') # Removed UIComponentManager dependency

    def toggle_statistics(self):
        if self.statistics_panel.is_visible:
            self.statistics_panel.hide_panel()
        # UIComponentManager.update_button_style(self.buttons['stats_button'], False, 'stats_button') # Removed UIComponentManager dependency
        else:
            self.statistics_panel.show_panel()
        # UIComponentManager.update_button_style(self.buttons['stats_button'], True, 'stats_button') # Removed UIComponentManager dependency

    def toggle_performance(self):
        if self.performance_panel.is_visible:
            self.performance_panel.hide_panel()
        # UIComponentManager.update_button_style(self.buttons['perf_button'], False, 'perf_button') # Removed UIComponentManager dependency
        else:
            self.performance_panel.show_panel()
        # UIComponentManager.update_button_style(self.buttons['perf_button'], True, 'perf_button') # Removed UIComponentManager dependency

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
        # # self.missile_status_labels = UIComponentManager.create_missile_status_labels( # Removed UIComponentManager dependency # Removed UIComponentManager dependency
        # self.sim_manager.drones, self.missile_status_layout # Fixed indentation and commented out)

    def change_mode(self, mode_text):
        for mode in Modes:
            if mode.value == mode_text:
                self.sim_modes.set_mode(mode)
                self.sim_modes.apply_mode_to_simulation(self.sim_manager.drones, self.sim_manager.target)
                self.movement_controller.sim_modes = self.sim_modes
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

    def start_simulation(self):
        """Start the simulation"""
        self.simulation_running = True
        self.timer.start()
        self.simulation_controller.start_simulation()
        print("🚁 Simulation started")
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.simulation_running = False
        self.timer.stop()
        self.simulation_controller.stop_simulation()
        print("⏹️ Simulation stopped")
    
    def _on_target_destroyed(self):
        """Handle target destroyed event"""
        print("🎯 Target destroyed!")
        if hasattr(self, 'alert_system'):
            self.alert_system.show_target_destroyed_alert()
    
    def _update_simulation(self):
        """Update simulation each frame"""
        if self.simulation_running:
            self.simulation_controller.update_simulation_step()
            self.update()  # Trigger repaint
