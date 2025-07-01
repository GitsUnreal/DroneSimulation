import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, QRect, Qt
from PyQt5.QtGui import QPainter, QColor, QFont
from AI.Drone import Drone 
from GUI.ControlPanel import ControlPanel
from AI.MainController import MainController
from GUI.MissileGUI import update_missiles
import random
import numpy as np

class MainWindow(QWidget):
    """
    Main window for the drone simulation application.
    This class sets up the main layout, control panel, 
    and manages the simulation of drones and obstacles.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Simulator")
        self.resize(1080, 720)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Create main layout
        main_layout = QVBoxLayout()

        # Create COMPACT control panel at the top
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        # Buttons in horizontal layout
        self.button = QPushButton("Start Simulation")
        self.button.setFixedSize(120, 25)  # Smaller buttons
        self.button.setStyleSheet("background-color: lightgreen; font-size: 12px; border-radius: 3px;")
        self.button.clicked.connect(self.toggle_simulation)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.setFixedSize(80, 25)  # Smaller buttons
        self.reset_button.setStyleSheet("background-color: lightcoral; font-size: 12px; border-radius: 3px;")
        self.reset_button.clicked.connect(self.reset_simulation)
        
        # Add buttons to control layout
        control_layout.addWidget(self.button)
        control_layout.addWidget(self.reset_button)
        control_layout.addStretch()  # Push everything to the left
        
        # Add control panel to main layout with minimal space
        main_layout.addLayout(control_layout)
        
        # Add spacer to push status panel to bottom
        main_layout.addStretch()
        
        # Create missile status panel at the bottom left
        status_layout = QVBoxLayout()
        status_layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        
        self.missile_status_labels = []  # List to hold individual drone status labels
        
        # Add status layout to main layout
        main_layout.addLayout(status_layout)
        main_layout.setContentsMargins(5, 5, 5, 5)  # Small margins
        main_layout.setSpacing(0)  # No spacing between elements
        
        # Set the layout
        self.setLayout(main_layout)

        # Initialize drones
        num_drones = max(0, min(2, 50))
        self.drones = [Drone([np.random.rand()*500, np.random.rand()*500],
                            [np.random.rand()*2-1, np.random.rand()*2-1], 
                            i) for i in range(num_drones)]

        # Create individual status labels for each drone
        for i, drone in enumerate(self.drones):
            label = QLabel(f"Drone {drone.id}: Missile 0/{drone.max_missiles} fired - Alive")
            label.setStyleSheet("font-size: 12px; color: green; background-color: rgba(255,255,255,150); padding: 2px; border-radius: 3px;")
            self.missile_status_labels.append(label)
            status_layout.addWidget(label)

        # Initialize obstacles, target, and base
        self.obstacles = [
            QRect(200, 150, 100, 50),
            QRect(350, 300, 100, 50),
        ]

        self.target = QRect(random.randint(400, 800), random.randint(100, 500), 20, 20)
        self.base = QRect(50, 50, 20, 20)  # Base position for drones

        self.movement_controller = MainController(self.drones, self.obstacles, self.target, self.base)

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_simulation)

        self.simulation_running = False

    def update_missile_display(self):
        """Update the missile count display for all drones with individual labels"""
        for i, (drone, label) in enumerate(zip(self.drones, self.missile_status_labels)):
            active_missiles = 0
            if hasattr(drone, 'missiles'):
                active_missiles = len([m for m in drone.missiles if m['active']])
            
            status = "Alive" if drone.alive else "Destroyed"
            
            # Update individual drone status
            label.setText(f"Drone {drone.id}: Missile {drone.missiles_fired}/{drone.max_missiles} fired, {active_missiles} active - {status}")
            
            # Change color based on drone status
            if drone.alive:
                label.setStyleSheet("font-size: 12px; color: green; background-color: rgba(255,255,255,150); padding: 2px; border-radius: 3px;")
            else:
                label.setStyleSheet("font-size: 12px; color: red; background-color: rgba(255,200,200,150); padding: 2px; border-radius: 3px;")

    def toggle_simulation(self):
        if self.simulation_running:
            self.timer.stop()
            self.button.setText("Start Simulation")
        else:
            self.timer.start()
            self.button.setText("Pause Simulation")
        self.simulation_running = not self.simulation_running

    def reset_simulation(self):
        """Reset the simulation to initial state"""
        # Stop the simulation if running
        if self.simulation_running:
            self.timer.stop()
            self.simulation_running = False
            self.button.setText("Start Simulation")
        
        # Reset drone position and state with proper synchronization
        for i, drone in enumerate(self.drones):
            # Reset to starting positions with some spread
            start_x = 50 + i * 40
            start_y = 50 + i * 30
            
            # Ensure position is synchronized properly
            drone.position = np.array([start_x, start_y], dtype=float)
            drone.x = start_x
            drone.y = start_y
            drone.velocity = np.array([0.0, 0.0])  # Reset velocity
            drone.alive = True
            drone.has_attacked = False 
            drone.reset_missiles()  # Reset missile count
            
            # Clear pathfinding data
            drone.current_path = []
            drone.current_waypoint_index = 0
            if hasattr(drone, 'current_path_timer'):
                drone.current_path_timer = 0
            
            print(f"Reset drone {i} to position ({start_x}, {start_y})")
                
        # Update missile display
        self.update_missile_display()
        
        # Generate new random target
        self.target = QRect(random.randint(400, 800), random.randint(100, 500), 20, 20)
        print(f"New target at ({self.target.x()}, {self.target.y()})")
        
        # Reinitialize movement controller with new target
        self.movement_controller = MainController(self.drones, self.obstacles, self.target, self.base)
        
        # Force a repaint
        self.update()
        
        print("Simulation reset!")

    def update_simulation(self):
        # Check for collisions with obstacles
        for drone in self.drones:
            if not drone.alive:
                continue
                
            # Check obstacle collisions
            for obs in self.obstacles:
                if obs.contains(int(drone.position[0]), int(drone.position[1])):
                    print(f"Drone {drone.id} destroyed by obstacle collision at ({drone.position[0]:.1f}, {drone.position[1]:.1f})")
                    drone.destroy()
                    break
            
            # Check drone-to-drone collisions
            if drone.alive:
                for other in self.drones:
                    if other is not drone and other.alive:
                        distance = np.linalg.norm(drone.position - other.position)
                        if distance < 20:  # Collision threshold
                            # print(f"Drone collision detected! Distance: {distance:.1f}")
                            # Optional: destroy both drones or just push them apart
                            # For now, let's just push them apart
                            direction = drone.position - other.position
                            if np.linalg.norm(direction) > 0:
                                direction = direction / np.linalg.norm(direction)
                                drone.position += direction * 2
                                other.position -= direction * 2
        
        # Use the movement controller for pathfinding
        self.movement_controller.move_drones()
        
        # Update missiles
        update_missiles(self.drones)
        
        # Update missile display
        self.update_missile_display()
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate drawing area (leave space for control panel at top and status at bottom)
        control_panel_height = 35  # Height reserved for control panel
        status_panel_height = 60   # Height reserved for status panel
        
        # Draw Drone with missile count
        painter.setBrush(QColor(0, 120, 215))
        for drone in self.drones:
            if drone.alive:
                # No offset needed since status is overlay
                draw_x = int(drone.x)
                draw_y = int(drone.y) + control_panel_height
                painter.drawEllipse(draw_x, draw_y, 20, 20)
                
                # Draw missile count next to drone
                painter.setPen(QColor(0, 0, 0))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(draw_x + 25, draw_y + 15, 
                               f"{drone.missiles_fired}/{drone.max_missiles}")

        # Draw Obstacles (adjust for control panel)
        painter.setBrush(QColor(200, 50, 50))
        for obstacle in self.obstacles:
            adjusted_obstacle = QRect(obstacle.x(), obstacle.y() + control_panel_height, 
                                    obstacle.width(), obstacle.height())
            painter.drawRect(adjusted_obstacle)

        # Draw Target (adjust for control panel)
        painter.setBrush(QColor(50, 200, 50))
        adjusted_target = QRect(self.target.x(), self.target.y() + control_panel_height, 
                              self.target.width(), self.target.height())
        painter.drawRect(adjusted_target)

        # Draw Base (adjust for control panel)
        painter.setBrush(QColor(0, 0, 0))  # Black base
        adjusted_base = QRect(self.base.x(), self.base.y() + control_panel_height, 
                            self.base.width(), self.base.height())
        painter.drawRect(adjusted_base)

        # Draw Missiles (adjust for control panel)
        painter.setBrush(QColor(255, 0, 0))  # Red missiles
        for drone in self.drones:
            if hasattr(drone, 'missiles'):
                for missile in drone.missiles:
                    if missile['active']:
                        # Ensure coordinates are integers and adjust for control panel
                        missile_x = int(round(float(missile['position'][0])))
                        missile_y = int(round(float(missile['position'][1]))) + control_panel_height
                        painter.drawEllipse(missile_x - 3, missile_y - 3, 6, 6)

        painter.end()

    def closeEvent(self, event):
        print("Main window closed.")
        event.accept()
