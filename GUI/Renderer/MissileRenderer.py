from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt
import numpy as np
import math

class MissileRenderer:
    def __init__(self):
        self.trail_fade_factor = 0.8
        
    def draw_missiles(self, painter: QPainter, missile_manager, offset_y: int):
        """Draw all missiles with enhanced effects"""
        for missile in missile_manager.get_active_missiles():
            self._draw_missile(painter, missile, offset_y)
            self._draw_missile_trail(painter, missile, offset_y)
        
        # Draw explosion effects
        for effect in missile_manager.explosion_effects:
            self._draw_explosion(painter, effect, offset_y)

    def _draw_missile(self, painter: QPainter, missile, offset_y: int):
        """Draw individual missile with type-specific appearance"""
        x, y = int(missile.position[0]), int(missile.position[1]) + offset_y
        
        # Choose color based on missile type
        if missile.missile_type.value == "homing":
            color = QColor(255, 165, 0)  # Orange
        elif missile.missile_type.value == "explosive":
            color = QColor(255, 0, 0)    # Red
        elif missile.missile_type.value == "piercing":
            color = QColor(0, 255, 255)  # Cyan
        else:
            color = QColor(255, 255, 0)  # Yellow (standard)
        
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(), 2))
        
        # Draw missile body
        if missile.state.value == "homing":
            # Draw larger, pulsing missile for homing
            size = 6 + int(2 * math.sin(missile.age * 10))
            painter.drawEllipse(x - size//2, y - size//2, size, size)
        else:
            painter.drawEllipse(x - 3, y - 3, 6, 6)
        
        # Draw direction indicator
        if np.linalg.norm(missile.velocity) > 0:
            vel_norm = missile.velocity / np.linalg.norm(missile.velocity)
            end_x = x + vel_norm[0] * 15
            end_y = y + vel_norm[1] * 15
            
            painter.setPen(QPen(color, 2))
            painter.drawLine(x, y, int(end_x), int(end_y))

    def _draw_missile_trail(self, painter: QPainter, missile, offset_y: int):
        """Draw missile trail effect"""
        if len(missile.trail_points) < 2:
            return
            
        for i, point in enumerate(missile.trail_points):
            alpha = int(255 * (i / len(missile.trail_points)) * 0.5)
            color = QColor(255, 255, 255, alpha)
            painter.setPen(QPen(color, 2))
            
            x, y = int(point[0]), int(point[1]) + offset_y
            painter.drawPoint(x, y)

    def _draw_explosion(self, painter: QPainter, effect: dict, offset_y: int):
        """Draw explosion effect"""
        if not effect['active']:
            return
            
        x, y = int(effect['position'][0]), int(effect['position'][1]) + offset_y
        radius = int(effect['radius'])
        intensity = effect['intensity']
        
        # Draw expanding circle with fading color
        alpha = int(255 * intensity)
        explosion_color = QColor(255, 100, 0, alpha)
        
        painter.setBrush(QBrush(explosion_color))
        painter.setPen(QPen(QColor(255, 255, 0, alpha), 3))
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)