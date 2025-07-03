from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

class SpeedControlWidget(QWidget):
    speed_changed = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Speed label
        self.speed_label = QLabel("Speed: 1.0x")
        layout.addWidget(self.speed_label)
        
        # Speed slider (0.1x to 5.0x)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)  # 0.1x
        self.speed_slider.setMaximum(50)  # 5.0x
        self.speed_slider.setValue(10)  # 1.0x
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        layout.addWidget(self.speed_slider)
        
        # Preset buttons
        presets = [(0.5, "0.5x"), (1.0, "1x"), (2.0, "2x"), (5.0, "5x")]
        for speed, text in presets:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, s=speed: self.set_speed(s))
            layout.addWidget(btn)
            
        self.setLayout(layout)
        
    def on_speed_changed(self, value):
        speed = value / 10.0
        self.speed_label.setText(f"Speed: {speed:.1f}x")
        self.speed_changed.emit(speed)
        
    def set_speed(self, speed):
        self.speed_slider.setValue(int(speed * 10))