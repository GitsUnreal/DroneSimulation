from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont

class AlertSystem:
    def __init__(self, parent):
        self.parent = parent
        self.alert_label = None
        self.alert_timer = QTimer()
        self.fade_animation = None
        self.alert_timer.timeout.connect(self.start_fade_out)
        
    def hide_alert(self):
        """Hide the current alert immediately"""
        if hasattr(self, 'alert_label') and self.alert_label is not None:
            if self.fade_animation:
                self.fade_animation.stop()
            self.alert_label.hide()
            self.alert_label.deleteLater()
            self.alert_label = None
        if hasattr(self, 'alert_timer') and self.alert_timer.isActive():
            self.alert_timer.stop()

    def start_fade_out(self):
        """Start the fade-out animation"""
        if hasattr(self, 'alert_label') and self.alert_label is not None:
            # Create opacity effect
            self.opacity_effect = QGraphicsOpacityEffect()
            self.alert_label.setGraphicsEffect(self.opacity_effect)
            
            # Create fade-out animation
            self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_animation.setDuration(800)  # 800ms fade out
            self.fade_animation.setStartValue(1.0)
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
            self.fade_animation.finished.connect(self.on_fade_finished)
            self.fade_animation.start()

    def on_fade_finished(self):
        """Called when fade animation is complete"""
        if hasattr(self, 'alert_label') and self.alert_label is not None:
            self.alert_label.hide()
            self.alert_label.deleteLater()
            self.alert_label = None

    def show_alert(self, text, border_color="#FFD700", duration=3000):
        """Show a custom alert with fade-in/fade-out animation"""
        
        # Hide any existing alert
        self.hide_alert()
        
        # Create a new alert label
        self.alert_label = QLabel(self.parent)
        self.alert_label.setText(text)
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.setWordWrap(True)
        
        # Clean, modern styling without unsupported properties
        self.alert_label.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(25, 25, 25, 250),
                    stop:0.5 rgba(35, 35, 35, 250),
                    stop:1 rgba(15, 15, 15, 250));
                color: white;
                border: 4px solid {border_color};
                border-radius: 25px;
                padding: 30px;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
        """)
        
        # Position the alert in the center of the parent window
        parent_rect = self.parent.rect()
        alert_width = 500
        alert_height = 150
        x = (parent_rect.width() - alert_width) // 2
        y = (parent_rect.height() - alert_height) // 2
        
        self.alert_label.setGeometry(x, y, alert_width, alert_height)
        
        # Create fade-in effect
        self.opacity_effect = QGraphicsOpacityEffect()
        self.alert_label.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        # Show and raise
        self.alert_label.show()
        self.alert_label.raise_()
        
        # Fade-in animation
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(500)  # Slightly longer fade in
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()
        
        # Start timer to auto-hide (subtract fade-in time)
        self.alert_timer.start(duration - 500)

    def show_drone_destroyed_alert(self, drone_id):
        """Show alert when a drone is destroyed"""
        alert_text = f"💥 DRONE {drone_id} DESTROYED! 💥"
        self.show_alert(alert_text, "#E74C3C", duration=3500)  # Red

    def show_all_missiles_fired_alert(self, drone_id):
        """Show alert when a drone fires all missiles"""
        alert_text = f"🚀 DRONE {drone_id} - ALL MISSILES FIRED! 🚀"
        self.show_alert(alert_text, "#F39C12", duration=2500)  # Orange

    def show_drone_landed_alert(self, drone_id):
        """Show alert when a drone lands safely"""
        alert_text = f"🏠 DRONE {drone_id} LANDED SAFELY 🏠"
        self.show_alert(alert_text, "#27AE60", duration=2000)  # Green

    def show_mission_complete_alert(self, drones):
        """Show alert when mission is complete"""
        alert_text = "🎯 MISSION COMPLETE! 🎯\nAll drones have returned to base."
        self.show_alert(alert_text, "#2ECC71", duration=4000)  # Bright Green