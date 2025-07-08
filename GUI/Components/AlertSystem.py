"""Alert system for GUI notifications"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer

class AlertSystem(QWidget):
    """System for displaying alerts and notifications"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.alerts = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.clear_old_alerts)
        self.timer.start(5000)  # Clear alerts every 5 seconds
        
    def init_ui(self):
        """Initialize the UI"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
    
    def add_alert(self, message, alert_type="info"):
        """Add an alert message"""
        alert_label = QLabel(f"{alert_type.upper()}: {message}")
        self.layout.addWidget(alert_label)
        self.alerts.append(alert_label)
        
        # Auto-remove after 5 seconds
        QTimer.singleShot(5000, lambda: self.remove_alert(alert_label))
    
    def remove_alert(self, alert_label):
        """Remove an alert"""
        if alert_label in self.alerts:
            self.layout.removeWidget(alert_label)
            alert_label.deleteLater()
            self.alerts.remove(alert_label)
    
    def clear_old_alerts(self):
        """Clear old alerts"""
        if len(self.alerts) > 5:  # Keep only 5 most recent alerts
            oldest = self.alerts.pop(0)
            self.layout.removeWidget(oldest)
            oldest.deleteLater()

    def show_alert(self, message, color="#FF0000", duration=3000):
        """Show a general alert with custom color and duration"""
        alert_label = QLabel(message)
        alert_label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 5px; background-color: rgba(255,255,255,200); border: 2px solid {color}; border-radius: 5px;")
        alert_label.setWordWrap(True)
        
        self.layout.addWidget(alert_label)
        self.alerts.append(alert_label)
        
        # Auto-remove after specified duration
        QTimer.singleShot(duration, lambda: self.remove_alert(alert_label))
    
    def show_drone_destroyed_alert(self, drone_id):
        """Show alert when drone is destroyed"""
        self.show_alert(f"🚁 Drone {drone_id} DESTROYED!", "#FF0000", 4000)
    
    def show_all_missiles_fired_alert(self, drone_id):
        """Show alert when drone has fired all missiles"""
        self.show_alert(f"🚀 Drone {drone_id}: All missiles fired!", "#FFA500", 3000)
    
    def show_drone_landed_alert(self, drone_id):
        """Show alert when drone lands"""
        self.show_alert(f"🛬 Drone {drone_id} landed at base", "#00AA00", 2000)
    
    def show_target_destroyed_alert(self):
        """Show alert when target is destroyed"""
        self.show_alert("🎯 TARGET DESTROYED! Mission Complete!", "#00FF00", 5000)
    
    def show_mission_start_alert(self):
        """Show alert when mission starts"""
        self.show_alert("🚁 Mission Started - Drones deploying!", "#0088FF", 2000)
