"""Renderer for radar displays"""
from .Renderer import Renderer
from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt

class RadarRenderer(Renderer):
    """Renders radar sweep and detected objects"""
    
    def __init__(self):
        super().__init__()
        self.radar_color = Qt.green
        
    def render(self, painter, radar_data):
        """Render radar display"""
        if not self.enabled:
            return
            
        painter.setPen(QPen(self.radar_color, 1, Qt.DashLine))
        
        # Render radar range circles
        for drone in radar_data.get('drones', []):
            if hasattr(drone, 'position'):
                x, y = drone.position
                range_radius = getattr(drone, 'radar_range', 100)
                painter.drawEllipse(int(x-range_radius), int(y-range_radius), 
                                  range_radius*2, range_radius*2)
    def toggle_radar(self):
        """Toggle radar display on/off"""
        self.enabled = not self.enabled
        return self.enabled
    
    def set_sweep_speed(self, speed_mode):
        """Set radar sweep speed"""
        speed_map = {
            "slow": 0.5,
            "normal": 1.0,
            "fast": 2.0,
            "very_fast": 3.0,
            "ultra_fast": 5.0
        }
        self.sweep_speed = speed_map.get(speed_mode, 1.0)
        print(f"Radar sweep speed set to: {speed_mode}")
