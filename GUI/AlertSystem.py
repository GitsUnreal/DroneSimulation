from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, QPropertyAnimation, QEasingCurve, Qt
from PyQt5.QtGui import QFont
import time

class AlertSystem:
    def __init__(self, parent):
        self.parent = parent
        self.alert_label = None
        self.fade_animation = None
        self.alert_timer = QTimer()
        self.alert_timer.setSingleShot(True)
        self.alert_timer.timeout.connect(self.hide_alert)
        
        self.create_alert_label()

    def create_alert_label(self):
        """Create the alert display label"""
        self.alert_label = QLabel(self.parent)
        self.alert_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                border: 3px solid #FFD700;
                border-radius: 10px;
                padding: 20px;
                font-size: 18px;
                font-weight: bold;
                text-align: center;
            }
        """)
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.hide()

    def show_mission_complete_alert(self, drones):
        """Show mission completion alert with statistics"""
        total_drones = len(drones)
        landed_count = sum(1 for drone in drones if hasattr(drone, 'has_landed') and drone.has_landed)
        destroyed_count = sum(1 for drone in drones if not drone.alive)
        missiles_fired = sum(drone.missiles_fired for drone in drones)
        
        if landed_count == total_drones:
            alert_text = f"""🎉 MISSION COMPLETE! 🎉
            
✅ All {total_drones} drones returned safely
🚀 {missiles_fired} missiles fired
⭐ Perfect execution!"""
            border_color = "#00FF00"
        elif destroyed_count > 0:
            alert_text = f"""⚠️ MISSION COMPLETE ⚠️
            
✅ {landed_count} drones returned
💥 {destroyed_count} drones lost
🚀 {missiles_fired} missiles fired
🎯 Objectives achieved with casualties"""
            border_color = "#FFFF00"
        else:
            alert_text = f"""🎯 MISSION COMPLETE 🎯
            
✅ Objectives achieved
🚀 {missiles_fired} missiles fired
🚁 {total_drones} drones operational"""
            border_color = "#4A90E2"
        
        self.show_alert(alert_text, border_color, duration=5000)

    def show_drone_destroyed_alert(self, drone_id):
        """Show alert when a drone is destroyed"""
        alert_text = f"💥 DRONE {drone_id} DESTROYED! 💥"
        self.show_alert(alert_text, "#FF0000", duration=2000)

    def show_all_missiles_fired_alert(self, drone_id):
        """Show alert when a drone fires all missiles"""
        alert_text = f"🚀 DRONE {drone_id} - ALL MISSILES FIRED! 🚀"
        self.show_alert(alert_text, "#FF8C00", duration=1500)

    def show_drone_landed_alert(self, drone_id):
        """Show alert when a drone lands"""
        alert_text = f"🏠 DRONE {drone_id} LANDED SAFELY 🏠"
        self.show_alert(alert_text, "#00FF00", duration=1500)

    def show_alert(self, text, border_color="#FFD700", duration=3000):
        """Show a custom alert with fade-in/fade-out animation"""
        self.alert_label.setText(text)
        self.alert_label.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(0, 0, 0, 180);
                color: white;
                border: 3px solid {border_color};
                border-radius: 10px;
                padding: 20px;
                font-size: 18px;
                font-weight: bold;
                text-align: center;
            }}
        """)
        
        # Position in center of parent
        parent_rect = self.parent.rect()
        self.alert_label.adjustSize()
        label_rect = self.alert_label.rect()
        x = (parent_rect.width() - label_rect.width()) // 2
        y = (parent_rect.height() - label_rect.height()) // 2
        self.alert_label.move(x, y)
        
        # Show with fade-in animation
        self.alert_label.show()
        self.fade_in()
        
        # Set timer to hide
        self.alert_timer.start(duration)

    def fade_in(self):
        """Animate fade-in effect"""
        self.opacity_effect = QGraphicsOpacityEffect()
        self.alert_label.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.start()

    def hide_alert(self):
        """Hide alert with fade-out animation"""
        if self.fade_animation:
            try:
                self.fade_animation.finished.disconnect()
            except TypeError:
                # Signal was already disconnected or never connected
                pass
    
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.finished.connect(self.alert_label.hide)
        self.fade_animation.start()