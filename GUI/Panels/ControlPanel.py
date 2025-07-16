from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QSlider, QCheckBox, QLabel, QApplication, QHBoxLayout
)
from PyQt5.QtCore import Qt

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Speed control slider
        self.speed_label = QLabel("Drone Speed:")

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(0, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)

        # Checkbox for obstacle avoidance
        self.avoid_obstacles_checkbox = QCheckBox("Show Obstacles")
        self.avoid_obstacles_checkbox.setChecked(True)
        layout.addWidget(self.avoid_obstacles_checkbox)

        self.setLayout(layout)

        # Connect signals
        self.speed_slider.valueChanged.connect(self.on_speed_change)

    def on_speed_change(self, value):
        self.speed_label.setText(f"Drone Speed: {value}")