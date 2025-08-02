
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMainWindow
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from Config.SimulationConfig import SimulationConfig
from .SimulationDrawingMixin import SimulationDrawingMixin

class SimulationCanvas(QWidget, SimulationDrawingMixin):
    """Custom widget for drawing the simulation"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setMinimumSize(800, 600)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        painter.scale(self.zoom_factor, self.zoom_factor)
        painter.translate(self.pan_offset.x() / self.zoom_factor, self.pan_offset.y() / self.zoom_factor)
        try:
            if getattr(self, 'show_grid', False):
                self.draw_grid(painter)
            if hasattr(self, 'sim_manager') and self.sim_manager:
                self.draw_simulation_elements(painter, self.sim_manager)
        except Exception as e:
            import traceback
            traceback.print_exc()
        finally:
            painter.end()
