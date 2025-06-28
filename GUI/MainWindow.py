import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer, QRect
from PyQt5.QtGui import QPainter, QColor
from GUI.Drone import Drone 
from GUI.ControlPanel import ControlPanel
from AI.Movementcontroller import MovementController
import random

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

        self.drones = [
            Drone(50, 50),
        ]

        self.obstacles = [
            QRect(200, 150, 100, 50),
            QRect(350, 300, 100, 50),
        ]

        self.target = QRect(random.randint(400, 800), random.randint(100, 500), 20, 20)

        self.movement_controller = MovementController(self.drones, self.obstacles, self.target)


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
        
        # Reset drone position and state
        for drone in self.drones:
            drone.x = 50
            drone.y = 50
            drone.alive = True
        
        # Generate new random target
        self.target = QRect(random.randint(400, 800), random.randint(100, 500), 20, 20)
        
        # Reinitialize movement controller with new target
        self.movement_controller = MovementController(self.drones, self.obstacles, self.target)
        
        # Force a repaint
        self.update()
        
        print("Simulation reset!")

    def update_simulation(self):
        # Check for collisions with obstacles
        for drone in self.drones:
            for obs in self.obstacles:
                if obs.contains(int(drone.x + drone.vx), int(drone.y + drone.vy)):
                    drone.destroy()
                    break
        
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
