import math
import random
import numpy as np
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient
from PyQt5.QtCore import QTimer, QRect

class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 0.2
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt  # Apply gravity
        self.lifetime -= dt
        
        # Fade out over time
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        self.color.setAlpha(max(0, alpha))
        
        return self.lifetime > 0

class ExplosionEffect:
    def __init__(self, x, y, intensity=1.0, radius=50.0, missile_type="standard"):
        self.x = x
        self.y = y
        self.intensity = intensity
        self.max_radius = radius  # Use configurable radius
        self.missile_type = missile_type
        self.particles = []
        self.active = True
        self.age = 0
        self.max_age = 3.0
        
        # Create particles based on explosion size
        num_particles = int(30 * intensity * (radius / 50.0))  # Scale particles by radius
        
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 80) * intensity * (radius / 50.0)  # Scale speed by radius
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Different particle types based on missile type
            if missile_type == "explosive":
                particle_type = random.choice(['fire', 'fire', 'smoke'])  # More fire
            elif missile_type == "piercing":
                particle_type = random.choice(['spark', 'spark', 'fire'])  # More sparks
            else:
                particle_type = random.choice(['fire', 'smoke', 'spark'])
                
            if particle_type == 'fire':
                color = QColor(255, random.randint(100, 255), 0, 255)
                size = random.uniform(3, 8)
                lifetime = random.uniform(0.8, 1.5)
            elif particle_type == 'smoke':
                gray = random.randint(50, 150)
                color = QColor(gray, gray, gray, 180)
                size = random.uniform(8, 15)
                lifetime = random.uniform(2.0, 3.0)
            else:  # spark
                color = QColor(255, 255, 200, 255)
                size = random.uniform(1, 3)
                lifetime = random.uniform(0.3, 0.8)
            
            particle = Particle(x, y, vx, vy, color, size, lifetime)
            self.particles.append(particle)
    
    def update(self, dt):
        self.age += dt
        
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Effect is done when all particles are gone or max age reached
        if not self.particles or self.age > self.max_age:
            self.active = False
        
        return self.active
    
    def draw(self, painter, offset_y=0):
        for particle in self.particles:
            painter.setBrush(QBrush(particle.color))
            painter.setPen(QPen(particle.color))
            painter.drawEllipse(
                int(particle.x - particle.size/2), 
                int(particle.y - particle.size/2 + offset_y),
                int(particle.size), 
                int(particle.size)
            )

class ExplosionManager:
    def __init__(self):
        self.explosions = []
    
    def add_explosion(self, x, y, intensity=1.0, radius=50.0, missile_type="standard"):
        """Add explosion with configurable radius and type"""
        explosion = ExplosionEffect(x, y, intensity, radius, missile_type)
        self.explosions.append(explosion)

    def update(self, dt):
        self.explosions = [exp for exp in self.explosions if exp.update(dt)]
    
    def draw_all(self, painter, offset_y=0):
        for explosion in self.explosions:
            explosion.draw(painter, offset_y)
    
    def clear(self):
        self.explosions.clear()

class ScreenFlash:
    def __init__(self):
        self.flash_alpha = 0
        self.flash_timer = 0
        self.flash_duration = 0.3
        
    def trigger_flash(self, intensity=1.0):
        self.flash_alpha = int(100 * intensity)
        self.flash_timer = 0
        
    def update(self, dt):
        if self.flash_alpha > 0:
            self.flash_timer += dt
            progress = self.flash_timer / self.flash_duration
            
            if progress >= 1.0:
                self.flash_alpha = 0
            else:
                self.flash_alpha = int(100 * (1 - progress))
    
    def draw(self, painter, width, height):
        if self.flash_alpha > 0:
            from PyQt5.QtGui import QColor
            painter.fillRect(0, 0, width, height, 
                           QColor(255, 255, 255, self.flash_alpha))