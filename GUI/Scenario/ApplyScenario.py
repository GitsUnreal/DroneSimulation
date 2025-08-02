from PyQt5.QtWidgets import QMessageBox, QApplication

from DroneSystem.MainController import MainController
from GUI.Components.UIComponentManager import UIComponentManager
from SimMode.Modes import SimModes, Modes

def apply_scenario_to_simulation(self, scenario_data: dict):
        """Apply scenario data to current simulation"""
        try:
            # Ensure base exists before proceeding
            if self.sim_manager.base is None:
                from PyQt5.QtCore import QRect
                from Config.SimulationConfig import SimulationConfig
                self.sim_manager.base = QRect(50, 50, SimulationConfig.BASE_SIZE, SimulationConfig.BASE_SIZE)
        
            # Reset simulation first
            self.reset_simulation()
            
            # Apply mission settings
            metadata = scenario_data.get('metadata', {})
            mission_type = metadata.get('mission_type', 'normal').lower()
            
            # Count drones in scenario
            items = scenario_data.get('items', [])
            scenario_drones = [item for item in items if item.get('type') == 'drone']
            num_drones_in_scenario = len(scenario_drones)
            
            # Set mode
            try:
                if mission_type == 'search_and_destroy' and hasattr(Modes, 'SEARCH_AND_DESTROY'):
                    self.sim_modes.set_mode(Modes.SEARCH_AND_DESTROY)
                elif mission_type == 'escort' and hasattr(Modes, 'ESCORT'):
                    self.sim_modes.set_mode(Modes.ESCORT)
                else:
                    self.sim_modes.set_mode(Modes.NORMAL)
            except Exception as e:
                self.sim_modes.set_mode(Modes.NORMAL)
            
            # Clear existing elements
            self.sim_manager.drones.clear()
            self.sim_manager.obstacles.clear()
            
            # Process items
            drone_count = 0
            for item in items:
                try:
                    item_type = item.get('type')
                    position = item.get('position', [100, 100])
                    if isinstance(position, (int, float)):
                        position = [position, position]
                    elif not isinstance(position, (list, tuple)):
                        position = [100, 100]
                    
                    if len(position) < 2:
                        position = position + [100] * (2 - len(position))
                    
                    properties = item.get('properties', {})
                    
                    if item_type == 'drone':
                        from DroneSystem.Core.Drone import Drone
                        
                        drone = Drone(
                            position=[float(position[0]), float(position[1])], 
                            velocity=[0.0, 0.0], 
                            drone_id=drone_count
                        )
                        
                        drone.max_missiles = properties.get('max_missiles', 2)
                        drone.formation_role = properties.get('formation_role', 'assault')
                        
                        self.sim_manager.drones.append(drone)
                        drone_count += 1
                        
                    elif item_type == 'target':
                        try:
                            from EnemySystem.Target import Target
                            
                            target_x = float(position[0])
                            target_y = float(position[1])
                            
                            target = Target(
                                target_id=1, 
                                position=[target_x, target_y],
                                height=properties.get('height', 30),
                                width=properties.get('width', 30),
                                hidden=properties.get('hidden', False)
                            )
                            
                            target.target_type = properties.get('target_type', 'standard')
                            target.health = properties.get('health', 100)
                            target.movement_pattern = properties.get('movement_pattern', 'stationary')
                            
                            if mission_type == 'escort':
                                target.is_vip = True
                                target.needs_escort = True
                            
                            self.sim_manager.target = target
                            
                        except Exception as e:
                            pass
                            
                    elif item_type == 'obstacle':
                        try:
                            from PyQt5.QtCore import QRect
                            
                            obs_x = int(float(position[0]))
                            obs_y = int(float(position[1]))
                            
                            obs_width = properties.get('width', properties.get('size', 40))
                            obs_height = properties.get('height', properties.get('size', 40))
                            
                            obs_width = max(int(obs_width), 20)
                            obs_height = max(int(obs_height), 20)
                            
                            obstacle = QRect(obs_x, obs_y, obs_width, obs_height)
                            self.sim_manager.obstacles.append(obstacle)
                            
                        except Exception as e:
                            fallback_obs = QRect(300 + len(self.sim_manager.obstacles) * 60, 300, 40, 40)
                            self.sim_manager.obstacles.append(fallback_obs)
                            
                    elif item_type == 'base':
                        try:
                            from PyQt5.QtCore import QRect
                            
                            base_x = int(float(position[0]))
                            base_y = int(float(position[1]))
                            base_capacity = properties.get('capacity', 10)
                            
                            base_size = max(base_capacity, 20)
                            self.sim_manager.base = QRect(base_x, base_y, base_size, base_size)
                            
                        except Exception as e:
                            if self.sim_manager.base is None:
                                self.sim_manager.base = QRect(50, 50, 20, 20)
                
                except Exception as e:
                    continue
    
            # Reinitialize movement controller
            try:
                self.movement_controller = MainController(
                    self.sim_manager.drones, 
                    self.sim_manager.obstacles, 
                    self.sim_manager.target, 
                    self.sim_manager.base,
                    self.sim_modes,
                    alert_system=self.alert_system
                )
                self.sim_manager.movement_controller = self.movement_controller
            except Exception as e:
                pass
            
            # Recreate missile status labels
            try:
                for label in self.missile_status_labels:
                    label.deleteLater()
                self.missile_status_labels = UIComponentManager.create_missile_status_labels(
                    self.sim_manager.drones, self.missile_status_layout
                )
            except Exception as e:
                pass
            
            # Update canvas
            try:
                self.canvas.sim_manager = self.sim_manager
                self.canvas.movement_controller = self.movement_controller
                self.canvas.renderer = self.renderer
                self.canvas.missile_renderer = self.missile_renderer
                self.canvas.radar_renderer = self.radar_renderer
                self.canvas.explosion_manager = self.explosion_manager
                self.canvas.screen_flash = self.screen_flash
                
                self.canvas.show_grid = self.show_grid
                self.canvas.show_paths = self.show_paths
                self.canvas.show_debug = self.show_debug
                
                self.canvas.update()
                self.canvas.repaint()
                QApplication.processEvents()
                
            except Exception as e:
                pass
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply scenario: {str(e)}")

        # Force canvas updates
        try:
            self.canvas.setMinimumSize(800, 600)
            self.canvas.resize(1080, 720)
            
            for i in range(3):
                self.canvas.update()
                self.canvas.repaint()
                QApplication.processEvents()
                
        except Exception as e:
            pass

    