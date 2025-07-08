"""Renderer for missiles"""
from .Renderer import Renderer
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import Qt

class MissileRenderer(Renderer):
    """Renders missiles in the simulation"""
    
    def __init__(self):
        super().__init__()
        self.missile_color = Qt.red
        
    def render(self, painter, missiles):
        """Render all missiles"""
        if not self.enabled or not missiles:
            return
            
        painter.setPen(QPen(self.missile_color, 2))
        painter.setBrush(QBrush(self.missile_color))
        
        for missile in missiles:
            if hasattr(missile, 'position'):
                x, y = missile.position
                size = getattr(missile, 'size', 5)
                painter.drawEllipse(int(x-size/2), int(y-size/2), size, size)
    def draw_missiles(self, painter, missile_manager, offset_y):
        """Draw missiles from missile manager"""
        if not self.enabled or not missile_manager:
            return
        
        missiles = getattr(missile_manager, 'missiles', [])
        
        for missile in missiles:
            if hasattr(missile, 'position') and hasattr(missile, 'active') and missile.active:
                x, y = missile.position
                size = getattr(missile, 'size', 5)
                painter.setBrush(self.missile_color)
                painter.drawEllipse(int(x-size/2), int(y+offset_y-size/2), size, size)
