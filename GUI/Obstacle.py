from PyQt5.QtCore import QRect

class Obstacle:
    def __init__(self, x, y, width, height, active=True):
        self.rect = QRect(x, y, width, height)
        self.active = active

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False

    def toggle(self):
        self.active = not self.active

    def contains(self, x, y):
        return self.active and self.rect.contains(x, y)

    def get_rect(self):
        return self.rect
