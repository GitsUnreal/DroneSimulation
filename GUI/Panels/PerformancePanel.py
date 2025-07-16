import time
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QFrame
from PyQt5.QtCore import Qt

class PerformancePanel(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.is_visible = False
        self.frame_times = []
        self.last_update_time = time.time()
        self.update_counter = 0
        
        self.init_ui()

    def init_ui(self):
        """Initialize the performance panel UI"""
        self.setFixedSize(250, 200)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 220);
                border: 2px solid #555;
                border-radius: 8px;
                color: white;
                font-family: 'Courier New';
            }
            QLabel {
                padding: 2px;
                border: none;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("⚡ Performance Metrics")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFD700; text-align: center;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #555;")
        layout.addWidget(separator)
        
        # Performance labels
        self.fps_label = QLabel("FPS: --")
        self.avg_fps_label = QLabel("Avg FPS: --")
        self.frame_time_label = QLabel("Frame Time: -- ms")
        self.cpu_usage_label = QLabel("CPU Usage: --%")
        self.memory_label = QLabel("Memory: -- MB")
        self.grid_ops_label = QLabel("Grid Operations: --")
        self.pathfinding_ops_label = QLabel("Pathfinding Ops: --")
        self.active_missiles_label = QLabel("Active Missiles: --")
        
        labels = [
            self.fps_label, self.avg_fps_label, self.frame_time_label,
            self.cpu_usage_label, self.memory_label, self.grid_ops_label,
            self.pathfinding_ops_label, self.active_missiles_label
        ]
        
        for label in labels:
            label.setStyleSheet("font-size: 10px; color: #E0E0E0;")
            layout.addWidget(label)
        
        self.setLayout(layout)
        self.hide()

    def show_panel(self):
        """Show the performance panel"""
        if self.parent:
            # Calculate position relative to parent
            x_pos = self.parent.width() - 270
            y_pos = 50
            
            # Set parent explicitly
            self.setParent(self.parent)
            
            # Move and show
            self.move(x_pos, y_pos)
            self.show()
            self.raise_()  # Bring to front
            self.is_visible = True
        else:
            print("PerformancePanel: No parent set!")

    def hide_panel(self):
        """Hide the performance panel"""
        self.hide()
        self.is_visible = False

    def update_metrics(self, drones, movement_controller):
        """Update all performance metrics"""
        current_time = time.time()
        frame_time = (current_time - self.last_update_time) * 1000  # Convert to ms
        self.frame_times.append(frame_time)
        
        # Keep only last 60 frame times for rolling average
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
        
        # Calculate FPS
        current_fps = 1000 / max(frame_time, 1)  # Avoid division by zero
        avg_fps = 1000 / max(sum(self.frame_times) / len(self.frame_times), 1)
        
        # Count active elements
        active_drones = sum(1 for drone in drones if drone.alive and not (hasattr(drone, 'has_landed') and drone.has_landed))
        total_missiles = sum(len([m for m in getattr(drone, 'missiles', []) if m['active']]) for drone in drones)
        pathfinding_active = sum(1 for drone in drones if hasattr(drone, 'current_path') and drone.current_path)
        
        # Get memory usage (simplified)
        import psutil
        import os
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent()
        
        # Grid operations (estimate)
        grid_cells = len(getattr(movement_controller, 'grid', {}))
        grid_ops = grid_cells * pathfinding_active
        
        # Update labels with color coding
        self.fps_label.setText(f"FPS: {current_fps:.1f}")
        self.avg_fps_label.setText(f"Avg FPS: {avg_fps:.1f}")
        self.frame_time_label.setText(f"Frame Time: {frame_time:.1f} ms")
        self.cpu_usage_label.setText(f"CPU Usage: {cpu_percent:.1f}%")
        self.memory_label.setText(f"Memory: {memory_mb:.1f} MB")
        self.grid_ops_label.setText(f"Grid Operations: {grid_ops}")
        self.pathfinding_ops_label.setText(f"Pathfinding Ops: {pathfinding_active}")
        self.active_missiles_label.setText(f"Active Missiles: {total_missiles}")
        
        # Color code based on performance
        self._apply_performance_colors(current_fps, cpu_percent, memory_mb)
        
        self.last_update_time = current_time
        self.update_counter += 1

    def _apply_performance_colors(self, fps, cpu, memory):
        """Apply color coding based on performance metrics"""
        # FPS color coding
        if fps >= 15:
            fps_color = "#00FF00"  # Green
        elif fps >= 10:
            fps_color = "#FFFF00"  # Yellow
        else:
            fps_color = "#FF0000"  # Red
        
        # CPU color coding
        if cpu <= 50:
            cpu_color = "#00FF00"  # Green
        elif cpu <= 80:
            cpu_color = "#FFFF00"  # Yellow
        else:
            cpu_color = "#FF0000"  # Red
        
        # Memory color coding
        if memory <= 100:
            mem_color = "#00FF00"  # Green
        elif memory <= 200:
            mem_color = "#FFFF00"  # Yellow
        else:
            mem_color = "#FF0000"  # Red
        
        self.fps_label.setStyleSheet(f"font-size: 10px; color: {fps_color};")
        self.cpu_usage_label.setStyleSheet(f"font-size: 10px; color: {cpu_color};")
        self.memory_label.setStyleSheet(f"font-size: 10px; color: {mem_color};")