from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen
from PyQt5.QtCore import Qt

class ZoomableSimulationCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        
        # REMOVE these problematic attributes that cause paint engine issues
        # self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        # self.setAttribute(Qt.WA_NoSystemBackground, True)
        
        # Instead, use these safer attributes
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StaticContents, True)
        
        # Initialize properties
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.pan_offset = [0, 0]
        
        # Initialize simulation references
        self.sim_manager = None
        self.movement_controller = None
        self.renderer = None
        self.missile_renderer = None
        self.radar_renderer = None
        self.explosion_manager = None
        self.screen_flash = None
        
        # Display options
        self.show_grid = False
        self.show_paths = False
        self.show_debug = False

    def paintEvent(self, event):
        """Paint the simulation canvas"""
        painter = QPainter(self)
        if not painter.isActive():
            return
            
        try:
            # Clear background
            painter.fillRect(self.rect(), QColor(240, 240, 240))
            
            # Apply zoom and pan
            painter.scale(self.zoom_factor, self.zoom_factor)
            painter.translate(self.pan_offset[0], self.pan_offset[1])
            
            # Draw simulation elements if available
            if self.sim_manager and self.renderer:
                # Draw static elements (obstacles, target, base)
                self.renderer.draw_static_elements(
                    painter, 0, 
                    self.sim_manager.obstacles, 
                    self.sim_manager.target, 
                    self.sim_manager.base
                )
                
                # Draw drones
                for drone in self.sim_manager.drones:
                    if drone.alive:
                        self.renderer.draw_drone_with_status(painter, drone, 0, 20)
                
                # Draw grid if enabled
                if self.show_grid and self.movement_controller:
                    self.renderer.draw_grid(painter, 0, self.movement_controller)
                
                # Draw paths if enabled
                if self.show_paths:
                    self.renderer.draw_paths(painter, 0, self.sim_manager.drones)
            
            # Draw missiles if available
            if (self.missile_renderer and self.movement_controller and 
                hasattr(self.movement_controller, 'missile_manager')):
                try:
                    missile_manager = self.movement_controller.missile_manager
                    if hasattr(missile_manager, 'get_active_missiles'):
                        active_missiles = missile_manager.get_active_missiles()
                        if active_missiles:
                            self.missile_renderer.render_missiles(painter, missile_manager)
                except Exception as e:
                    pass
            
            # ALWAYS DRAW RADAR - NO CONDITIONS
            if (self.radar_renderer and self.sim_manager and 
                hasattr(self.sim_manager, 'drones') and self.sim_manager.drones):
                try:
                    # Force radar to be enabled
                    self.radar_renderer.radar_enabled = True
                    
                    # Update radar detection every frame
                    visible_obstacles = self.radar_renderer.update_radar(
                        self.sim_manager.obstacles,
                        self.sim_manager.target,
                        self.sim_manager.drones
                    )
                    
                    # Draw radar overlay
                    self.radar_renderer.draw_radar(
                        painter,
                        self.sim_manager.drones,
                        self.sim_manager.obstacles,
                        0
                    )
                    
                except Exception as e:
                    print(f"Error drawing radar: {e}")
                    
        except Exception as e:
            print(f"Error in paintEvent: {e}")
        finally:
            painter.end()

    def reset_view(self):
        """Reset view to default"""
        self.zoom_factor = 1.0
        self.pan_offset = [0, 0]
        self.update()

    def fit_to_view(self):
        """Fit content to view"""
        # Calculate bounds of all simulation elements
        if self.sim_manager and self.sim_manager.drones:
            min_x = min(drone.position[0] for drone in self.sim_manager.drones)
            max_x = max(drone.position[0] for drone in self.sim_manager.drones)
            min_y = min(drone.position[1] for drone in self.sim_manager.drones)
            max_y = max(drone.position[1] for drone in self.sim_manager.drones)
            
            # Add padding
            padding = 50
            content_width = max_x - min_x + 2 * padding
            content_height = max_y - min_y + 2 * padding
            
            # Calculate zoom to fit
            zoom_x = self.width() / content_width
            zoom_y = self.height() / content_height
            self.zoom_factor = min(zoom_x, zoom_y, self.max_zoom)
            
            # Center content
            self.pan_offset = [
                (self.width() / self.zoom_factor - content_width) / 2 + padding - min_x,
                (self.height() / self.zoom_factor - content_height) / 2 + padding - min_y
            ]
            
            self.update()