"""
Window management and UI layout setup
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from GUI.Components.UIComponentManager import UIComponentManager
from GUI.Canvas.SimulationCanvas import SimulationCanvas
from Config.SimulationConfig import SimulationConfig

class WindowManager:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def init_window_properties(self):
        """Initialize basic window properties"""
        self.main_window.setWindowTitle("Drone Simulator")
        self.main_window.resize(SimulationConfig.WINDOW_WIDTH, SimulationConfig.WINDOW_HEIGHT)
        self.main_window.setStyleSheet("background-color: #f0f0f0;")
    
    def setup_ui_layout(self, callbacks):
        """Setup the main UI layout"""
        # Create central widget
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Create control bar
        try:
            control_bar, buttons, mode_combo, speed_combo = UIComponentManager.create_control_bar(callbacks)
            main_layout.addLayout(control_bar)
            
            # Store references
            self.main_window.buttons = buttons
            self.main_window.mode_combo = mode_combo
            self.main_window.speed_combo = speed_combo
            
        except Exception as e:
            print(f"Error creating control bar: {e}")
            from PyQt5.QtWidgets import QPushButton
            test_button = QPushButton("Test Button")
            main_layout.addWidget(test_button)
        
        # Add simulation canvas
        self.main_window.simulation_canvas = SimulationCanvas(self.main_window)
        main_layout.addWidget(self.main_window.simulation_canvas)

        # Bottom status area
        bottom_layout = QHBoxLayout()
        self.main_window.missile_status_layout = QVBoxLayout()
        self.main_window.missile_status_layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        
        bottom_layout.addLayout(self.main_window.missile_status_layout)
        bottom_layout.addStretch()
        
        main_layout.addLayout(bottom_layout)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)
