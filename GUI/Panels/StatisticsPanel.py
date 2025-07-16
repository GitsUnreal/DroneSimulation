from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt
import time

class StatisticsPanel(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.is_visible = False
        self.mission_start_time = None
        self.total_missiles_fired = 0
        self.drones_destroyed = 0
        self.successful_landings = 0
        
        self.init_ui()

    def init_ui(self):
        """Initialize the statistics panel UI"""
        self.setFixedWidth(300)
        self.setMinimumHeight(400)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(20, 20, 40, 220);
                border: 2px solid #4A90E2;
                border-radius: 8px;
                color: white;
                font-family: 'Arial';
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Title
        title = QLabel("📊 Mission Statistics")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4A90E2; text-align: center;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Mission Info Section
        mission_frame = self._create_section("Mission Info")
        layout.addWidget(mission_frame, stretch=1)
        
        # Drone Stats Section
        drone_frame = self._create_section("Drone Statistics")
        layout.addWidget(drone_frame, stretch=2)
        
        # Performance Section
        perf_frame = self._create_section("Performance")
        layout.addWidget(perf_frame, stretch=1)
        
        self.setLayout(layout)
        self.hide()

    def _create_section(self, title):
        """Create a section with title and labels"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("QFrame { border: 1px solid #555; border-radius: 4px; }")
        
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(6, 6, 6, 6)
        
        # Section title
        section_title = QLabel(title)
        section_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #FFD700;")
        layout.addWidget(section_title)
        
        if title == "Mission Info":
            self.mission_time_label = QLabel("Mission Time: 00:00")
            self.mission_status_label = QLabel("Status: In Progress")
            self.completion_label = QLabel("Completion: 0%")
            
            layout.addWidget(self.mission_time_label)
            layout.addWidget(self.mission_status_label)
            layout.addWidget(self.completion_label)
            
        elif title == "Drone Statistics":
            self.total_drones_label = QLabel("Total Drones: 0")
            self.active_drones_label = QLabel("Active: 0")
            self.landed_drones_label = QLabel("Landed: 0")
            self.destroyed_drones_label = QLabel("Destroyed: 0")
            self.missiles_fired_label = QLabel("Missiles Fired: 0")
            
            layout.addWidget(self.total_drones_label)
            layout.addWidget(self.active_drones_label)
            layout.addWidget(self.landed_drones_label)
            layout.addWidget(self.destroyed_drones_label)
            layout.addWidget(self.missiles_fired_label)
            
        elif title == "Performance":
            self.pathfinding_efficiency_label = QLabel("Pathfinding Efficiency: 100%")
            self.collision_rate_label = QLabel("Collision Rate: 0%")
            self.mission_efficiency_label = QLabel("Mission Efficiency: 100%")
            
            layout.addWidget(self.pathfinding_efficiency_label)
            layout.addWidget(self.collision_rate_label)
            layout.addWidget(self.mission_efficiency_label)
        
        # Style all labels
        for i in range(1, layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QLabel):
                widget.setStyleSheet("font-size: 10px; color: #E0E0E0; padding: 1px;")
        
        frame.setLayout(layout)
        return frame

    def show_panel(self):
        """Show the statistics panel"""
        if self.parent:
            # Set parent explicitly
            self.setParent(self.parent)
            
            # Move and show
            self.move(20, 50)
            self.show()
            self.raise_()  # Bring to front
            self.is_visible = True
            
            if self.mission_start_time is None:
                self.mission_start_time = time.time()
        else:
            print("StatisticsPanel: No parent set!")

    def hide_panel(self):
        """Hide the statistics panel"""
        self.hide()
        self.is_visible = False

    def update_statistics(self, drones, movement_controller):
        """Update all statistics"""
        if not self.is_visible:
            return
        
        # Mission timing
        if self.mission_start_time:
            elapsed = time.time() - self.mission_start_time
            minutes, seconds = divmod(int(elapsed), 60)
            self.mission_time_label.setText(f"Mission Time: {minutes:02d}:{seconds:02d}")
        
        # Drone counts
        total_drones = len(drones)
        active_drones = sum(1 for drone in drones if drone.alive and not (hasattr(drone, 'has_landed') and drone.has_landed))
        landed_drones = sum(1 for drone in drones if hasattr(drone, 'has_landed') and drone.has_landed)
        destroyed_drones = sum(1 for drone in drones if not drone.alive)
        
        # Mission progress
        total_missiles_possible = sum(drone.max_missiles for drone in drones)
        total_missiles_fired = sum(drone.missiles_fired for drone in drones)
        completion_percentage = (total_missiles_fired / total_missiles_possible * 100) if total_missiles_possible > 0 else 0
        
        # Mission status
        if landed_drones == total_drones:
            status = "✅ Complete"
            status_color = "#00FF00"
        elif destroyed_drones > 0:
            status = "⚠️ Casualties"
            status_color = "#FFFF00"
        elif total_missiles_fired > 0:
            status = "🎯 Combat"
            status_color = "#FF8C00"
        else:
            status = "🚁 Deploying"
            status_color = "#4A90E2"
        
        # Performance metrics
        pathfinding_active = sum(1 for drone in drones if hasattr(drone, 'current_path') and drone.current_path)
        pathfinding_efficiency = 100 - (pathfinding_active / max(active_drones, 1) * 100)
        
        # Update labels
        self.total_drones_label.setText(f"Total Drones: {total_drones}")
        self.active_drones_label.setText(f"Active: {active_drones}")
        self.landed_drones_label.setText(f"Landed: {landed_drones}")
        self.destroyed_drones_label.setText(f"Destroyed: {destroyed_drones}")
        self.missiles_fired_label.setText(f"Missiles Fired: {total_missiles_fired}/{total_missiles_possible}")
        self.completion_label.setText(f"Completion: {completion_percentage:.1f}%")
        
        self.mission_status_label.setText(f"Status: {status}")
        self.mission_status_label.setStyleSheet(f"font-size: 10px; color: {status_color}; padding: 1px;")
        
        self.pathfinding_efficiency_label.setText(f"Pathfinding Efficiency: {pathfinding_efficiency:.1f}%")
        self.collision_rate_label.setText(f"Collision Rate: {(destroyed_drones/total_drones*100):.1f}%")
        self.mission_efficiency_label.setText(f"Mission Efficiency: {completion_percentage:.1f}%")

    def reset_statistics(self):
        """Reset all statistics for a new mission"""
        self.mission_start_time = time.time()
        self.total_missiles_fired = 0
        self.drones_destroyed = 0
        self.successful_landings = 0