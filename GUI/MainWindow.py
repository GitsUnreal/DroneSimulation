import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer, QRect
from PyQt5.QtGui import QPainter, QColor
from GUI.Drone import Drone 
from GUI.ControlPanel import ControlPanel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Simulator")
        self.resize(1080, 720)

        main_layout = QVBoxLayout()

        self.control_panel = ControlPanel()
        main_layout.addWidget(self.control_panel)

        self.button = QPushButton("Start Simulation")
        self.button.clicked.connect(self.toggle_simulation)
        main_layout.addWidget(self.button)
        self.setLayout(main_layout)

        self.drones = [
            Drone(50, 50),
            Drone(100, 100),
            Drone(150, 150),
        ]

        self.obstacles = [
            QRect(200, 150, 100, 50),
            QRect(350, 300, 80, 30),
        ]

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_simulation)

        self.simulation_running = False

    def toggle_simulation(self):
        if self.simulation_running:
            self.timer.stop()
            self.button.setText("Launch Drones")
        else:
            self.timer.start()
            self.button.setText("Pause Simulation")
        self.simulation_running = not self.simulation_running

    def update_simulation(self):
        for drone in self.drones:
            drone.update(self.obstacles, self.width(), self.height())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(0, 120, 215))
        for drone in self.drones:
            painter.drawEllipse(int(drone.x), int(drone.y), 20, 20)

        painter.setBrush(QColor(200, 50, 50))
        for obstacle in self.obstacles:
            painter.drawRect(obstacle)

    def closeEvent(self, event):
        print("Main window closed.")
        event.accept()
