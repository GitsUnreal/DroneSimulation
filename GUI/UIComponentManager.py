from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QComboBox
from PyQt5.QtCore import Qt
from Config.SimulationConfig import SimulationConfig
from SimMode.Modes import Modes

class UIComponentManager:
    """Manages UI component creation and styling"""
    
    @staticmethod
    def create_button(text, size, color_key, callback=None):
        """Create a standardized button"""
        button = QPushButton(text)
        button.setFixedSize(*size)
        color = SimulationConfig.COLORS.get(color_key, 'lightgray')
        button.setStyleSheet(f"background-color: {color}; font-size: 10px; border-radius: 3px;")
        
        if callback:
            button.clicked.connect(callback)
        
        return button
    
    @staticmethod
    def create_control_bar(callbacks):
        """Create the main control bar with all buttons"""
        control_bar = QHBoxLayout()
        
        # Main simulation controls
        start_button = UIComponentManager.create_button(
            "Start Simulation", (120, 25), 'start_button', callbacks['toggle_simulation']
        )
        start_button.setStyleSheet("background-color: lightgreen; font-size: 12px; border-radius: 3px;")
        
        reset_button = UIComponentManager.create_button(
            "Reset", (80, 25), 'reset_button', callbacks['reset_simulation']
        )
        reset_button.setStyleSheet("background-color: lightcoral; font-size: 12px; border-radius: 3px;")
        
        # Visual toggle buttons
        buttons_config = [
            ('Grid', (50, 25), 'grid_button', 'toggle_grid'),
            ('Paths', (50, 25), 'path_button', 'toggle_paths'),
            ('Debug', (50, 25), 'debug_button', 'toggle_debug'),
            ('Stats', (50, 25), 'stats_button', 'toggle_statistics'),
            ('Perf', (50, 25), 'perf_button', 'toggle_performance'),
            ('Radar', (50, 25), 'radar_button', 'toggle_radar'),
        ]
        
        buttons = {'start_button': start_button, 'reset_button': reset_button}
        
        for text, size, color_key, callback_key in buttons_config:
            button = UIComponentManager.create_button(text, size, color_key, callbacks[callback_key])
            buttons[color_key] = button
        
        # Mode selection dropdown
        mode_combo = QComboBox()
        mode_combo.addItems([mode.value for mode in Modes])
        mode_combo.currentTextChanged.connect(callbacks['change_mode'])
        
        # Add all to layout
        for button in buttons.values():
            control_bar.addWidget(button)
        control_bar.addWidget(mode_combo)
        control_bar.addStretch()
        
        return control_bar, buttons, mode_combo
    
    @staticmethod
    def create_missile_status_labels(drones, layout):
        """Create missile status labels for all drones"""
        labels = []
        for drone in drones:
            label = QLabel(f"Drone {drone.drone_id}: 0/2 missiles fired, 0 active - Alive")
            label.setStyleSheet(
                "font-size: 12px; color: green; background-color: rgba(255,255,255,150); "
                "padding: 2px; border-radius: 3px;"
            )
            layout.addWidget(label)
            labels.append(label)
        return labels
    
    @staticmethod
    def update_button_style(button, active, color_key):
        """Update button style based on active state"""
        color = SimulationConfig.COLORS['active_button'] if active else SimulationConfig.COLORS[color_key]
        button.setStyleSheet(f"background-color: {color}; font-size: 10px; border-radius: 3px;")