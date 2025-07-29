from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import QRect

class SimulationDrawingMixin:
    def draw_simulation_elements(self, painter: QPainter, sim_manager):
        """
        Draw base, obstacles, drones, missiles, and target on the simulation canvas.
        """
        # Draw base
        if sim_manager.base:
            painter.setBrush(QBrush(QColor(0, 255, 0)))
            painter.drawRect(sim_manager.base)
        # Draw obstacles
        painter.setBrush(QBrush(QColor(139, 69, 19)))
        for obstacle in sim_manager.obstacles:
            painter.drawRect(obstacle)
        # Draw drones
        painter.setBrush(QBrush(QColor(0, 0, 255)))
        for drone in sim_manager.drones:
            drone_rect = QRect(int(drone.position[0]) - 10, int(drone.position[1]) - 10, 20, 20)
            painter.drawEllipse(drone_rect)
        # Draw missiles (from missile_manager if available)
        missiles = []
        if hasattr(sim_manager, 'missiles') and sim_manager.missiles:
            missiles = sim_manager.missiles
        elif hasattr(sim_manager, 'movement_controller') and hasattr(sim_manager.movement_controller, 'missile_manager'):
            missile_manager = sim_manager.movement_controller.missile_manager
            if hasattr(missile_manager, 'get_active_missiles'):
                missiles = missile_manager.get_active_missiles()
        if missiles:
            painter.setBrush(QBrush(QColor(255, 255, 0)))
            for missile in missiles:
                missile_pos = getattr(missile, 'position', [0, 0])
                missile_rect = QRect(int(missile_pos[0]) - 5, int(missile_pos[1]) - 5, 10, 10)
                painter.drawEllipse(missile_rect)
        # Draw target (show if not hidden or if spotted by radar)
        target = sim_manager.target
        show_target = False
        if target:
            if not getattr(target, 'hidden', False):
                show_target = True
            elif getattr(target, 'spotted_by_radar', False):
                show_target = True
        if show_target:
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            target_pos = getattr(target, 'position', [0, 0])
            target_rect = QRect(int(target_pos[0]) - 15, int(target_pos[1]) - 15, 30, 30)
            painter.drawEllipse(target_rect)

        # Draw radar if radar_renderer is present
        if hasattr(self, 'radar_renderer') and self.radar_renderer:
            try:
                self.radar_renderer.draw_radar(
                    painter,
                    getattr(sim_manager, 'drones', []),
                    getattr(sim_manager, 'obstacles', []),
                    0
                )
            except Exception:
                pass
