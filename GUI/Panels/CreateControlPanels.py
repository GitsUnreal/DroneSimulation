from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from GUI.Components.UIComponentManager import UIComponentManager

def create_control_panel(self):
        """Create the control panel with buttons and settings"""
        panel = QWidget()
        layout = QHBoxLayout()
        panel.setLayout(layout)
        
        # Start/Pause button
        start_button = QPushButton("Start")
        start_button.setObjectName("start_button")
        start_button.clicked.connect(self.toggle_simulation)
        layout.addWidget(start_button)
        
        # Reset button
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_simulation)
        layout.addWidget(reset_button)
        
        # Grid toggle button
        grid_btn = QPushButton("Grid")
        grid_btn.setCheckable(True)
        grid_btn.clicked.connect(self.toggle_grid)
        layout.addWidget(grid_btn)
        
        # Paths toggle button
        paths_btn = QPushButton("Paths")
        paths_btn.setCheckable(True)
        paths_btn.clicked.connect(self.toggle_paths)
        layout.addWidget(paths_btn)
        
        # Debug toggle button
        debug_btn = QPushButton("Debug")
        debug_btn.setCheckable(True)
        debug_btn.clicked.connect(self.toggle_debug)
        layout.addWidget(debug_btn)
        
        # Performance toggle button
        perf_btn = QPushButton("Perf")
        perf_btn.setCheckable(True)
        perf_btn.clicked.connect(self.toggle_performance)
        layout.addWidget(perf_btn)
        
        # Stats toggle button
        stats_btn = QPushButton("Stats")
        stats_btn.setCheckable(True)
        stats_btn.clicked.connect(self.toggle_stats)
        layout.addWidget(stats_btn)
        
        # REMOVED: Radar button - radar is now always active
        
        # Editor button
        editor_btn = QPushButton("Editor")
        editor_btn.clicked.connect(self.open_scenario_editor)
        layout.addWidget(editor_btn)
        
        # Create dropdown for modes
        mode_dropdown = UIComponentManager.create_mode_dropdown(self.change_mode)
        layout.addWidget(mode_dropdown)
        
        # Create dropdown for radar speed (kept for controlling sweep speed)
        speed_dropdown = UIComponentManager.create_radar_speed_dropdown(self.change_radar_speed)
        layout.addWidget(speed_dropdown)
        
        # Store buttons reference without radar button
        self.buttons = {
            'start_button': start_button,
            'reset_button': reset_button,
            'grid_button': grid_btn,
            'paths_button': paths_btn,
            'debug_button': debug_btn,
            'perf_button': perf_btn,
            'stats_button': stats_btn,
            'editor_button': editor_btn,
            'mode_dropdown': mode_dropdown,
            'speed_dropdown': speed_dropdown
        }
        
        return panel