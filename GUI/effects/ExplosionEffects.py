"""Explosion effects for the GUI"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer
import random
import math

class ExplosionManager:
    """Manages explosion effects"""
    
    def __init__(self):
        self.explosions = []
        
    def add_explosion(self, x, y, size=50):
        """Add an explosion at position"""
        explosion = {
            'x': x,
            'y': y,
            'size': size,
            'max_size': size,
            'lifetime': 1.0,  # seconds
            'age': 0.0
        }
        self.explosions.append(explosion)
    
    def update(self, dt):
        """Update all explosions"""
        for explosion in self.explosions[:]:
            explosion['age'] += dt
            if explosion['age'] >= explosion['lifetime']:
                self.explosions.remove(explosion)
            else:
                # Expand explosion
                progress = explosion['age'] / explosion['lifetime']
                explosion['size'] = explosion['max_size'] * (1 + progress)
    
    def render(self, painter):
        """Render all explosions"""
        for explosion in self.explosions:
            progress = explosion['age'] / explosion['lifetime']
            alpha = int(255 * (1 - progress))
            
            color = QColor(255, 100, 0, alpha)  # Orange with fading alpha
            painter.setBrush(color)
            painter.setPen(color)
            
            size = explosion['size']
            x = explosion['x'] - size/2
            y = explosion['y'] - size/2
            
            painter.drawEllipse(int(x), int(y), int(size), int(size))

class ScreenFlash:
    """Screen flash effect"""
    
    def __init__(self):
        self.flash_active = False
        self.flash_alpha = 0
        
    def trigger_flash(self, color=QColor(255, 255, 255)):
        """Trigger a screen flash"""
        self.flash_active = True
        self.flash_alpha = 100
        self.flash_color = color
    
    def update(self, dt):
        """Update flash effect"""
        if self.flash_active:
            self.flash_alpha -= 200 * dt  # Fade out
            if self.flash_alpha <= 0:
                self.flash_active = False
                self.flash_alpha = 0
    
    def render(self, painter, width, height):
        """Render flash effect"""
        if self.flash_active:
            color = QColor(self.flash_color)
            color.setAlpha(int(self.flash_alpha))
            painter.fillRect(0, 0, width, height, color)