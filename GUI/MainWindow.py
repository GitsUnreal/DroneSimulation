import sys
import random
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, QRect, Qt
from PyQt5.QtGui import QPainter, QColor, QFont

from AI.Drone import Drone 
from AI.MainController import MainController
from GUI.MissileGUI import update_missiles

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Simulator")
        self.resize(1080, 720)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.control_panel_height = 35

        self.init_layout()
        self.init_simulation()

    def init_layout(self):
        """Set up the UI layout."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Top control bar
        control_bar = QHBoxLayout()
        self.start_button = QPushButton("Start Simulation")
        self.start_button.setFixedSize(120, 25)
        self.start_button.setStyleSheet("background-color: lightgreen; font-size: 12px; border-radius: 3px;")
        self.start_button.clicked.connect(self.toggle_simulation)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setFixedSize(80, 25)
        self.reset_button.setStyleSheet("background-color: lightcoral; font-size: 12px; border-radius: 3px;")
        self.reset_button.clicked.connect(self.reset_simulation)

        control_bar.addWidget(self.start_button)
        control_bar.addWidget(self.reset_button)
        control_bar.addStretch()

        main_layout.addLayout(control_bar)
        main_layout.addStretch()

        # Missile status display (bottom-left)
        self.status_layout = QVBoxLayout()
        self.status_layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        main_layout.addLayout(self.status_layout)

        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

    def init_simulation(self):
        """Initialize simulation objects and controller."""
        num_drones = 2  # Can be changed
        self.drones = [
            Drone(
                [np.random.rand() * 500, np.random.rand() * 500],
                [np.random.rand() * 2 - 1, np.random.rand() * 2 - 1],
                i
            )
            for i in range(num_drones)
        ]

        self.missile_status_labels = []
        for drone in self.drones:
            label = QLabel(f"Drone {drone.drone_id}: Missile 0/{drone.max_missiles} fired - Alive")
            label.setStyleSheet("font-size: 12px; color: green; background-color: rgba(255,255,255,150); padding: 2px; border-radius: 3px;")
            self.status_layout.addWidget(label)
            self.missile_status_labels.append(label)

        self.obstacles = [
            QRect(200, 150, 100, 50),
            QRect(350, 300, 100, 50),
        ]
        self.target = self.random_target()
        self.base = QRect(50, 50, 20, 20)

        self.movement_controller = MainController(self.drones, self.obstacles, self.target, self.base)

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_simulation)

        self.simulation_running = False

    def random_target(self):
        return QRect(random.randint(400, 800), random.randint(100, 500), 20, 20)

    def toggle_simulation(self):
        self.simulation_running = not self.simulation_running
        if self.simulation_running:
            self.timer.start()
            self.start_button.setText("Pause Simulation")
        else:
            self.timer.stop()
            self.start_button.setText("Start Simulation")

    def reset_simulation(self):
        if self.simulation_running:
            self.timer.stop()
            self.simulation_running = False
            self.start_button.setText("Start Simulation")

        for i, drone in enumerate(self.drones):
            start_x = 50 + i * 40
            start_y = 50 + i * 30
            drone.position = np.array([start_x, start_y], dtype=float)
            drone.x, drone.y = start_x, start_y
            drone.velocity = np.zeros(2)
            drone.alive = True
            drone.has_attacked = False
            drone.reset_missiles()
            drone.current_path = []
            drone.current_waypoint_index = 0
            if hasattr(drone, 'current_path_timer'):
                drone.current_path_timer = 0
            print(f"Reset drone {i} to position ({start_x}, {start_y})")

        self.target = self.random_target()
        print(f"New target at ({self.target.x()}, {self.target.y()})")
        self.movement_controller = MainController(self.drones, self.obstacles, self.target, self.base)
        self.update_missile_display()
        self.update()

    def update_simulation(self):
        for drone in self.drones:
            if not drone.alive:
                continue

            for obs in self.obstacles:
                if obs.contains(int(drone.position[0]), int(drone.position[1])):
                    print(f"Drone {drone.drone_id} destroyed by obstacle at ({drone.position[0]:.1f}, {drone.position[1]:.1f})")
                    drone.destroy()
                    break

            for other in self.drones:
                if other is not drone and other.alive:
                    dist = np.linalg.norm(drone.position - other.position)
                    if dist < 20:
                        direction = drone.position - other.position
                        if np.linalg.norm(direction) > 0:
                            direction /= np.linalg.norm(direction)
                            drone.position += direction * 2
                            other.position -= direction * 2

        self.movement_controller.update_drones()
        update_missiles(self.drones)
        self.update_missile_display()
        self.update()

    def update_missile_display(self):
        for drone, label in zip(self.drones, self.missile_status_labels):
            active_missiles = len([m for m in getattr(drone, 'missiles', []) if m['active']])
            status_text = f"Drone {drone.drone_id}: Missile {drone.missiles_fired}/{drone.max_missiles} fired, {active_missiles} active - {'Alive' if drone.alive else 'Destroyed'}"
            label.setText(status_text)
            label.setStyleSheet(
                f"font-size: 12px; color: {'green' if drone.alive else 'red'}; background-color: rgba(255,255,255,150); padding: 2px; border-radius: 3px;"
            )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        offset_y = self.control_panel_height

        # Drones
        painter.setBrush(QColor(0, 120, 215))
        for drone in self.drones:
            if drone.alive:
                draw_x, draw_y = int(drone.x), int(drone.y) + offset_y
                painter.drawEllipse(draw_x, draw_y, 20, 20)
                painter.setPen(QColor(0, 0, 0))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(draw_x + 25, draw_y + 15, f"{drone.missiles_fired}/{drone.max_missiles}")

        # Obstacles
        painter.setBrush(QColor(200, 50, 50))
        for obs in self.obstacles:
            adjusted = QRect(obs.x(), obs.y() + offset_y, obs.width(), obs.height())
            painter.drawRect(adjusted)

        # Target
        painter.setBrush(QColor(50, 200, 50))
        target_adj = QRect(self.target.x(), self.target.y() + offset_y, self.target.width(), self.target.height())
        painter.drawRect(target_adj)

        # Base
        painter.setBrush(QColor(0, 0, 0))
        base_adj = QRect(self.base.x(), self.base.y() + offset_y, self.base.width(), self.base.height())
        painter.drawRect(base_adj)

        # Missiles
        painter.setBrush(QColor(255, 0, 0))
        for drone in self.drones:
            for missile in getattr(drone, 'missiles', []):
                if missile['active']:
                    mx = int(round(missile['position'][0]))
                    my = int(round(missile['position'][1])) + offset_y
                    painter.drawEllipse(mx - 3, my - 3, 6, 6)

    def closeEvent(self, event):
        print("Main window closed.")
        event.accept()
