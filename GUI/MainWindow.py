import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtGui import QPainter

from GUI.MissileGUI import update_missiles
from GUI.DebugPanel import DebugPanel
from GUI.StatusChecker import StatusChecker
from GUI.Renderer import Renderer
from GUI.SimulationManager import SimulationManager
from GUI.PerformancePanel import PerformancePanel
from GUI.StatisticsPanel import StatisticsPanel
from GUI.AlertSystem import AlertSystem
from GUI.MissileRenderer import MissileRenderer
from AI.Drone import Drone
from AI.MainController import MainController
from EnemyAI.Target import target

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Simulator")
        self.resize(1080, 720)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.control_panel_height = 35

        # Initialize components
        self.sim_manager = SimulationManager()
        self.debug_panel = DebugPanel(self)
        self.status_checker = StatusChecker()
        self.renderer = Renderer()
        self.missile_renderer = MissileRenderer()

        # Add new monitoring components
        self.performance_panel = PerformancePanel(self)
        self.statistics_panel = StatisticsPanel(self)
        self.alert_system = AlertSystem(self)

        # Visual toggles
        self.show_grid = False
        self.show_paths = False
        self.show_debug = False

        # Initialize simulation state
        self.simulation_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.setInterval(50)  # 50ms = 20 FPS
        
        # Initialize missile status labels list
        self.missile_status_labels = []

        self.init_layout()
        self.init_simulation()

    def init_layout(self):
        """Set up the UI layout."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Top control bar
        control_bar = self.create_control_bar()
        main_layout.addLayout(control_bar)
        main_layout.addStretch()

        # Bottom status area - ENHANCED
        bottom_layout = QHBoxLayout()
        
        # Left side - Missile status display
        self.missile_status_layout = QVBoxLayout()
        self.missile_status_layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        
        # Right side - for any other bottom-right elements
        right_bottom_layout = QVBoxLayout()
        right_bottom_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        bottom_layout.addLayout(self.missile_status_layout)
        bottom_layout.addStretch()
        bottom_layout.addLayout(right_bottom_layout)
        
        main_layout.addLayout(bottom_layout)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

    def create_control_bar(self):
        """Create the control button bar with new monitoring buttons"""
        control_bar = QHBoxLayout()
        
        # Simulation controls
        self.start_button = QPushButton("Start Simulation")
        self.start_button.setFixedSize(120, 25)
        self.start_button.setStyleSheet("background-color: lightgreen; font-size: 12px; border-radius: 3px;")
        self.start_button.clicked.connect(self.toggle_simulation)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setFixedSize(80, 25)
        self.reset_button.setStyleSheet("background-color: lightcoral; font-size: 12px; border-radius: 3px;")
        self.reset_button.clicked.connect(self.reset_simulation)

        # Visual toggles
        self.grid_button = QPushButton("Grid")
        self.grid_button.setFixedSize(50, 25)
        self.grid_button.setStyleSheet("background-color: lightblue; font-size: 10px; border-radius: 3px;")
        self.grid_button.clicked.connect(self.toggle_grid)

        self.path_button = QPushButton("Paths")
        self.path_button.setFixedSize(50, 25)
        self.path_button.setStyleSheet("background-color: lightyellow; font-size: 10px; border-radius: 3px;")
        self.path_button.clicked.connect(self.toggle_paths)

        self.debug_button = QPushButton("Debug")
        self.debug_button.setFixedSize(50, 25)
        self.debug_button.setStyleSheet("background-color: lightgray; font-size: 10px; border-radius: 3px;")
        self.debug_button.clicked.connect(self.toggle_debug)

        # Add monitoring buttons
        self.stats_button = QPushButton("Stats")
        self.stats_button.setFixedSize(50, 25)
        self.stats_button.setStyleSheet("background-color: lightcyan; font-size: 10px; border-radius: 3px;")
        self.stats_button.clicked.connect(self.toggle_statistics)

        self.perf_button = QPushButton("Perf")
        self.perf_button.setFixedSize(50, 25)
        self.perf_button.setStyleSheet("background-color: lightpink; font-size: 10px; border-radius: 3px;")
        self.perf_button.clicked.connect(self.toggle_performance)

        control_bar.addWidget(self.start_button)
        control_bar.addWidget(self.reset_button)
        control_bar.addWidget(self.grid_button)
        control_bar.addWidget(self.path_button)
        control_bar.addWidget(self.debug_button)
        control_bar.addWidget(self.stats_button)
        control_bar.addWidget(self.perf_button)
        control_bar.addStretch()

        return control_bar

    def init_simulation(self, num_drones=2):
        """Initialize simulation objects and controller."""
        
        # Create obstacles FIRST
        self.obstacles = [
            QRect(200, 150, 100, 50),
            QRect(350, 300, 100, 50),
        ]
        
        # Create drones with valid positions
        self.drones = []
        for i in range(num_drones):
            # Find valid spawn position for drone
            valid_position = self.find_valid_position(width=20, height=20, margin=30)
            
            # Add some offset for multiple drones
            if i > 0:
                # Try to space drones apart
                for attempt in range(10):
                    test_pos = (valid_position[0] + i * 40, valid_position[1] + i * 30)
                    if self.is_position_valid(test_pos, width=20, height=20, margin=30):
                        valid_position = test_pos
                        break
            
            drone = Drone(
                list(valid_position),  # Convert tuple to list
                [np.random.rand() * 2 - 1, np.random.rand() * 2 - 1],
                i
            )
            
            self.drones.append(drone)
            print(f"Spawned drone {i} at safe position {valid_position}")

        # Create target with valid position
        self._create_target_with_valid_position()
        
        self.base = QRect(50, 50, 20, 20)  # Base position is usually safe
        
        # Update sim_manager with our created objects
        self.sim_manager.drones = self.drones
        self.sim_manager.obstacles = self.obstacles
        self.sim_manager.target = self.target
        self.sim_manager.base = self.base
        
        # Create movement controller
        self.movement_controller = MainController(self.drones, self.obstacles, self.target, self.base)
        self.sim_manager.movement_controller = self.movement_controller
        
        # Clear existing missile status labels
        for label in getattr(self, 'missile_status_labels', []):
            label.deleteLater()
    
        # Create missile status labels in bottom-left layout
        self.missile_status_labels = []
        for i, drone in enumerate(self.drones):
            label = QLabel(f"Drone {drone.drone_id}: 0/2 missiles fired, 0 active - Alive", self)
            label.setStyleSheet("font-size: 12px; color: green; background-color: rgba(255,255,255,150); padding: 2px; border-radius: 3px;")
            
            # Add to the missile status layout (bottom-left)
            self.missile_status_layout.addWidget(label)
            self.missile_status_labels.append(label)

    def _create_target_with_valid_position(self):
        """Create a target in a valid position"""
        import random
        
        # Create different types of targets
        target_type = random.choice(["static", "linear", "circular", "waypoint", "random"])
        
        # Find valid position for target
        valid_position = self.find_valid_position(width=20, height=20, margin=40)
        
        if target_type == "static":
            self.target = target(target_id=1, position=valid_position, height=20, width=20)
        elif target_type == "linear":
            self.target = target(target_id=1, position=valid_position, height=20, width=20, is_moving_target=True)
            self.target.set_linear_movement(direction=[1, 0.5], speed=3.0)
        elif target_type == "circular":
            # For circular targets, make sure the circle doesn't intersect obstacles
            center_pos = self.find_valid_position(width=160, height=160, margin=80)  # Larger area for circle
            self.target = target(target_id=1, position=center_pos, height=20, width=20, is_moving_target=True)
            self.target.set_circular_movement(center=center_pos, radius=60, angular_speed=0.03)
        elif target_type == "waypoint":
            self.target = target(target_id=1, position=valid_position, height=20, width=20, is_moving_target=True)
            # Generate valid waypoints
            self._set_valid_waypoints(self.target, num_waypoints=6)
        elif target_type == "random":
            self.target = target(target_id=1, position=valid_position, height=20, width=20, is_moving_target=True)
            self.target.set_random_movement(direction_change_interval=2.0, speed=2.5)
        
        print(f"Created {target_type} target at safe position {valid_position}")

    def _set_valid_waypoints(self, target_obj, num_waypoints=6):
        """Generate valid waypoints that don't intersect obstacles"""
        valid_waypoints = []
        
        for _ in range(num_waypoints):
            waypoint_pos = self.find_valid_position(width=20, height=20, margin=30)
            valid_waypoints.append(np.array(waypoint_pos, dtype=float))
        
        target_obj.movement_pattern = "waypoint"
        target_obj.waypoints = valid_waypoints
        target_obj.current_waypoint_index = 0
        target_obj.path_complete = False
        
        print(f"Target {target_obj.target_id} valid waypoints: {valid_waypoints}")

    def toggle_simulation(self):
        """Toggle simulation start/pause"""
        self.simulation_running = not self.simulation_running
        if self.simulation_running:
            self.timer.start()
            self.start_button.setText("Pause Simulation")
        else:
            self.timer.stop()
            self.start_button.setText("Start Simulation")

    def reset_simulation(self):
        """Reset all drones and create new target"""
    
        # Clear existing missile status labels before creating new ones
        for label in getattr(self, 'missile_status_labels', []):
            label.deleteLater()
        self.missile_status_labels = []
    
        # Reset drones to safe positions
        for i, drone in enumerate(self.drones):
            # Find valid position for each drone
            valid_position = self.find_valid_position(width=20, height=20, margin=30)
            
            # Add offset for multiple drones
            if i > 0:
                for attempt in range(10):
                    test_pos = (valid_position[0] + i * 40, valid_position[1] + i * 30)
                    if self.is_position_valid(test_pos, width=20, height=20, margin=30):
                        valid_position = test_pos
                        break
            
            drone.position = np.array(valid_position, dtype=float)
            drone.x, drone.y = valid_position[0], valid_position[1]
            drone.velocity = np.zeros(2)
            drone.alive = True
            drone.has_attacked = False
            drone.has_landed = False
            
            if hasattr(drone, 'returning_to_base'):
                drone.returning_to_base = False

            drone.reset_missiles()
            drone.current_path = []
            drone.current_waypoint_index = 0
            if hasattr(drone, 'current_path_timer'):
                drone.current_path_timer = 0
            
            print(f"Reset drone {i} to safe position {valid_position}")

        # Reset target
        if self.target:
            self.target.destroyed = False

        # Create new target with valid position
        self._create_target_with_valid_position()
        
        self.movement_controller = MainController(self.drones, self.obstacles, self.target, self.base)

        # Reinitialize missile status labels after reset
        for i, drone in enumerate(self.drones):
            label = QLabel(f"Drone {drone.drone_id}: 0/2 missiles fired, 0 active - Alive", self)
            label.setStyleSheet("font-size: 12px; color: green; background-color: rgba(255,255,255,150); padding: 2px; border-radius: 3px;")
            self.missile_status_layout.addWidget(label)
            self.missile_status_labels.append(label)

    def update_simulation(self):
        """Enhanced simulation update with target destruction handling"""
        self.sim_manager.handle_collisions()
        
        # Get update results including target destruction status
        update_result = self.sim_manager.movement_controller.update_drones()
        
        update_missiles(self.sim_manager.drones)
        self.update_missile_display()
        
        # Handle target destruction
        if update_result and update_result.get('target_destroyed'):
            self.handle_target_destroyed()
        
        # Run periodic checks
        mission_complete, collisions, stuck = self.status_checker.run_periodic_checks(
            self.sim_manager.drones, 
            self.sim_manager.obstacles, 
            self.toggle_simulation
        )
        
        # Update debug info if enabled
        if self.show_debug:
            self.debug_panel.update_info(self.sim_manager.drones, self.sim_manager.movement_controller)
        
        # Update monitoring panels
        if self.performance_panel.is_visible:
            self.performance_panel.update_metrics(self.sim_manager.drones, self.sim_manager.movement_controller)
        
        if self.statistics_panel.is_visible:
            self.statistics_panel.update_statistics(self.sim_manager.drones, self.sim_manager.movement_controller)
        
        # Check for alerts
        self.check_for_alerts()
        
        self.update()

    def handle_target_destroyed(self):
        """Handle target destruction event"""
        print("🎯 TARGET DESTROYED! Mission objective complete!")
        
        # Show target destroyed alert
        self.alert_system.show_alert(
            "🎯 TARGET DESTROYED! 🎯\n\nMission Objective Complete!\nDrones returning to base...", 
            "#00FF00", 
            duration=4000
        )
        
        # Mark all active drones to return to base immediately
        for drone in self.sim_manager.drones:
            if drone.alive and not (hasattr(drone, 'has_landed') and drone.has_landed):
                if not hasattr(drone, 'returning_to_base'):
                    drone.has_attacked = True  # Force return to base behavior
                    print(f"Drone {drone.drone_id} ordered to return to base after target destruction")
        
        # Optionally pause simulation after a delay
        QTimer.singleShot(2000, self.pause_after_target_destroyed)

    def pause_after_target_destroyed(self):
        """Pause simulation after target is destroyed (optional)"""
        # Uncomment if you want to auto-pause after target destruction
        # if self.simulation_running:
        #     self.toggle_simulation()
        #     print("Simulation paused after target destruction")
        pass

    def check_for_alerts(self):
        """Check for events that should trigger alerts"""
        for drone in self.sim_manager.drones:
            # Check if drone just destroyed
            if not drone.alive and not hasattr(drone, '_destruction_alerted'):
                self.alert_system.show_drone_destroyed_alert(drone.drone_id)
                drone._destruction_alerted = True
            
            # Check if drone just fired all missiles
            if drone.missiles_fired >= drone.max_missiles and not hasattr(drone, '_missiles_alerted'):
                self.alert_system.show_all_missiles_fired_alert(drone.drone_id)
                drone._missiles_alerted = True
            
            # Check if drone just landed
            if hasattr(drone, 'has_landed') and drone.has_landed and not hasattr(drone, '_landing_alerted'):
                self.alert_system.show_drone_landed_alert(drone.drone_id)
                drone._landing_alerted = True

    def update_missile_display(self):
        """Update missile status labels"""
        for drone, label in zip(self.sim_manager.drones, self.missile_status_labels):
            active_missiles = len([m for m in getattr(drone, 'missiles', []) if m['active']])
            
            if drone.alive:
                status = "Alive"
            elif hasattr(drone, 'has_landed') and drone.has_landed:
                status = "Landed"
            else:
                status = "Destroyed"
            
            status_text = f"Drone {drone.drone_id}: Missile {drone.missiles_fired}/{drone.max_missiles} fired, {active_missiles} active - {status}"
            label.setText(status_text)
            label.setStyleSheet(
                f"font-size: 12px; color: {'green' if drone.alive else 'red'}; background-color: rgba(255,255,255,150); padding: 2px; border-radius: 3px;"
            )

    def paintEvent(self, event):
        """Main painting method"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate offset for control bar
        offset_y = 50

        # Draw existing elements
        self.renderer.draw_static_elements(painter, offset_y, 
                                         self.sim_manager.obstacles, 
                                         self.sim_manager.target, 
                                         self.sim_manager.base)

        # Draw grid if enabled - FIX: use self.show_grid instead of self.grid_visible
        if self.show_grid:
            self.renderer.draw_grid(painter, offset_y, self.sim_manager.movement_controller)

        # Draw drones
        for drone in self.sim_manager.drones:
            self.renderer.draw_drone_with_status(painter, drone, offset_y)

        # Draw paths if enabled - FIX: use self.show_paths instead of self.paths_visible
        if self.show_paths:
            self.renderer.draw_paths(painter, offset_y, self.sim_manager.drones)

        # NEW missile rendering using MissileRenderer
        if hasattr(self.sim_manager.movement_controller, 'missile_manager'):
            self.missile_renderer.draw_missiles(
                painter, 
                self.sim_manager.movement_controller.missile_manager, 
                offset_y
            )

    def get_active_drones(self):
        """Get list of drones that should be visible in simulation"""
        return [drone for drone in self.sim_manager.drones if drone.alive and not (hasattr(drone, 'has_landed') and drone.has_landed)]

    # Toggle methods
    def toggle_grid(self):
        self.show_grid = not self.show_grid
        button_color = "lightgreen" if self.show_grid else "lightblue"
        self.grid_button.setStyleSheet(f"background-color: {button_color}; font-size: 10px; border-radius: 3px;")
        self.update()
        print(f"Grid overlay: {'ON' if self.show_grid else 'OFF'}")

    def toggle_paths(self):
        self.show_paths = not self.show_paths
        button_color = "lightgreen" if self.show_paths else "lightyellow"
        self.path_button.setStyleSheet(f"background-color: {button_color}; font-size: 10px; border-radius: 3px;")
        self.update()
        print(f"Path visualization: {'ON' if self.show_paths else 'OFF'}")

    def toggle_debug(self):
        self.show_debug = not self.show_debug
        button_color = "lightgreen" if self.show_debug else "lightgray"
        self.debug_button.setStyleSheet(f"background-color: {button_color}; font-size: 10px; border-radius: 3px;")
        
        if self.show_debug:
            self.debug_panel.create_panel()
        else:
            self.debug_panel.hide_panel()
        
        print(f"Debug panel: {'ON' if self.show_debug else 'OFF'}")

    def toggle_statistics(self):
        """Toggle statistics panel"""
        if self.statistics_panel.is_visible:
            self.statistics_panel.hide_panel()
            self.stats_button.setStyleSheet("background-color: lightcyan; font-size: 10px; border-radius: 3px;")
        else:
            self.statistics_panel.show_panel()
            self.stats_button.setStyleSheet("background-color: lightgreen; font-size: 10px; border-radius: 3px;")

    def toggle_performance(self):
        """Toggle performance panel"""
        if self.performance_panel.is_visible:
            self.performance_panel.hide_panel()
            self.perf_button.setStyleSheet("background-color: lightpink; font-size: 10px; border-radius: 3px;")
        else:
            self.performance_panel.show_panel()
            self.perf_button.setStyleSheet("background-color: lightgreen; font-size: 10px; border-radius: 3px;")

    def closeEvent(self, event):
        print("Main window closed.")
        event.accept()

    def is_position_valid(self, position, width=20, height=20, margin=10):
        """Check if a position is valid (not inside obstacles with margin)"""
        x, y = position
        
        # Check bounds
        if x < 50 or x > 1000 or y < 100 or y > 600:
            return False
        
        # Check collision with obstacles
        for obstacle in self.obstacles:
            # Add margin around obstacles
            if (obstacle.x() - margin <= x <= obstacle.x() + obstacle.width() + margin and
                obstacle.y() - margin <= y <= obstacle.y() + obstacle.height() + margin):
                return False
        
        return True

    def find_valid_position(self, width=20, height=20, margin=10, max_attempts=50):
        """Find a valid spawn position that doesn't overlap with obstacles"""
        import random
        
        for _ in range(max_attempts):
            x = random.randint(50, 1000)
            y = random.randint(100, 600)
            
            if self.is_position_valid((x, y), width, height, margin):
                return (x, y)
        
        # Fallback to safe positions if no valid position found
        safe_positions = [
            (75, 125), (100, 150), (125, 175), (150, 200),  # Top-left area
            (900, 500), (850, 450), (800, 400), (750, 350)  # Bottom-right area
        ]
        
        for pos in safe_positions:
            if self.is_position_valid(pos, width, height, margin):
                return pos
        
        # Last resort - return a position far from obstacles
        return (75, 125)
