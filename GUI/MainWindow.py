import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer, QRect
from PyQt5.QtGui import QPainter, QColor
from AI.Drone import Drone 
from GUI.ControlPanel import ControlPanel
from AI.MainController import MainController
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

        main_layout = QVBoxLayout()

        # self.control_panel = ControlPanel()
        # main_layout.addWidget(self.control_panel, 1)

        # Create button layout
        button_layout = QVBoxLayout()
        
        self.button = QPushButton("Start Simulation")
        self.button.setFixedSize(150, 30)
        self.button.setStyleSheet("background-color: lightgreen; font-size: 16px; border-radius: 5px;")
        self.button.clicked.connect(self.toggle_simulation)
        button_layout.addWidget(self.button)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.setFixedSize(150, 30)
        self.reset_button.setStyleSheet("background-color: lightcoral; font-size: 16px; border-radius: 5px;")
        self.reset_button.clicked.connect(self.reset_simulation)
        button_layout.addWidget(self.reset_button)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        num_drones = max(0, min(2, 50))  # clamps the number to 5
        self.drones = [Drone([np.random.rand()*500, np.random.rand()*500],
                            [np.random.rand()*2-1, np.random.rand()*2-1], 
                            i) for i in range(num_drones)]  # Added drone ID as third parameter

        self.obstacles = [
            QRect(200, 150, 100, 50),
            QRect(350, 300, 100, 50),
        ]

        self.target = QRect(random.randint(400, 800), random.randint(100, 500), 20, 20)

        self.movement_controller = MainController(self.drones, self.obstacles, self.target)


        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_simulation)

        self.simulation_running = False

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
            
            print(f"Reset drone {i} to position ({start_x}, {start_y})")
                    
        # Reinitialize movement controller with new target
        self.movement_controller = MainController(self.drones, self.obstacles, self.target)
        
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
                            print(f"Drone collision detected! Distance: {distance:.1f}")
                            # Optional: destroy both drones or just push them apart
                            # For now, let's just push them apart
                            direction = drone.position - other.position
                            if np.linalg.norm(direction) > 0:
                                direction = direction / np.linalg.norm(direction)
                                drone.position += direction * 2
                                other.position -= direction * 2
        
        # Use the movement controller for pathfinding
        self.movement_controller.move_drones()
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw Drone
        painter.setBrush(QColor(0, 120, 215))
        for drone in self.drones:
            painter.drawEllipse(int(drone.x), int(drone.y), 20, 20)

        # Draw Obstacles
        painter.setBrush(QColor(200, 50, 50))
        for obstacle in self.obstacles:
            painter.drawRect(obstacle)

        # Draw Target
        painter.setBrush(QColor(50, 200, 50))
        painter.drawRect(self.target)
        painter.end()

    def closeEvent(self, event):
        print("Main window closed.")
        event.accept()
