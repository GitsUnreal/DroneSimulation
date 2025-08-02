
from DroneSystem.MainController import MainController

from GUI.Scenario.ApplyScenario import apply_scenario_to_simulation

class create_file_menu():
    import json
    from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication

    def export_current_simulation_as_scenario(self):
        """Export current simulation state as a scenario"""
        scenario_data = {
            'metadata': {
                'name': f"Exported Scenario {len(self.main_window.sim_manager.drones)} drones",
                'mission_type': self.main_window.sim_modes.current_mode.value.lower(),
                'difficulty': 'Normal',
                'time_limit': 300,
                'map_width': 1080,
                'map_height': 720,
                'grid_size': 20
            },
            'items': []
        }
        for i, drone in enumerate(self.main_window.sim_manager.drones):
            scenario_data['items'].append({
                'type': 'drone',
                'position': [int(drone.position[0]), int(drone.position[1])],
                'properties': {
                    'drone_id': i,
                    'max_missiles': getattr(drone, 'max_missiles', 2),
                    'formation_role': getattr(drone, 'formation_role', 'assault')
                }
            })
        if self.main_window.sim_manager.target:
            t = self.main_window.sim_manager.target
            scenario_data['items'].append({
                'type': 'target',
                'position': [int(t.position[0]), int(t.position[1])],
                'properties': {
                    'target_type': getattr(t, 'target_type', 'standard'),
                    'health': getattr(t, 'health', 100),
                    'hidden': getattr(t, 'hidden', False)
                }
            })
        for obstacle in self.main_window.sim_manager.obstacles:
            scenario_data['items'].append({
                'type': 'obstacle',
                'position': [getattr(obstacle, 'x', lambda: obstacle.x())(), getattr(obstacle, 'y', lambda: obstacle.y())()],
                'properties': {
                    'size': getattr(obstacle, 'size', 40),
                    'destructible': False
                }
            })
        if self.main_window.sim_manager.base:
            base = self.main_window.sim_manager.base
            scenario_data['items'].append({
                'type': 'base',
                'position': [base.x(), base.y()],
                'properties': {'capacity': 10}
            })
        return scenario_data

    def convert_sim_to_scenario(self, sim_data):
        # Similar to your previous MainWindow logic
        scenario_data = {
            'metadata': {
                'name': sim_data.get('metadata', {}).get('mission_name', 'Converted Simulation'),
                'mission_type': sim_data.get('metadata', {}).get('mission_type', 'search_and_destroy'),
                'difficulty': 'Normal',
                'time_limit': 300,
                'map_width': sim_data.get('config', {}).get('map_width', 1080),
                'map_height': sim_data.get('config', {}).get('map_height', 720),
                'grid_size': sim_data.get('config', {}).get('grid_size', 20)
            },
            'items': []
        }
        for drone_data in sim_data.get('drones', []):
            scenario_data['items'].append({
                'type': 'drone',
                'position': drone_data.get('position', [100, 100]),
                'properties': {
                    'drone_id': drone_data.get('drone_id', 0),
                    'max_missiles': drone_data.get('max_missiles', 2),
                    'formation_role': drone_data.get('formation_role', 'assault')
                }
            })
        for target_data in sim_data.get('targets', []):
            scenario_data['items'].append({
                'type': 'target',
                'position': target_data.get('position', [500, 500]),
                'properties': {
                    'target_type': target_data.get('target_type', 'standard'),
                    'health': target_data.get('health', 100),
                    'hidden': target_data.get('hidden', False)
                }
            })
        for obs_data in sim_data.get('obstacles', []):
            if isinstance(obs_data, dict):
                pos = obs_data.get('position', [400, 300])
                size = obs_data.get('size', 40)
            elif isinstance(obs_data, (list, tuple)) and len(obs_data) >= 2:
                pos = [obs_data[0], obs_data[1]]
                size = obs_data[2] if len(obs_data) > 2 else 40
            else:
                pos = [400, 300]
                size = 40
            scenario_data['items'].append({
                'type': 'obstacle',
                'position': pos,
                'properties': {'size': size, 'destructible': False}
            })
        bases_data = sim_data.get('bases', [])
        if bases_data:
            if isinstance(bases_data, dict):
                base_pos = bases_data.get('position', [50, 50])
                capacity = bases_data.get('capacity', 10)
            elif isinstance(bases_data, list) and len(bases_data) > 0:
                first_base = bases_data[0]
                base_pos = first_base.get('position', [50, 50])
                capacity = first_base.get('capacity', 10)
            else:
                base_pos = [50, 50]
                capacity = 10
            scenario_data['items'].append({
                'type': 'base',
                'position': base_pos,
                'properties': {'capacity': capacity}
            })
        else:
            scenario_data['items'].append({
                'type': 'base',
                'position': [50, 50],
                'properties': {'capacity': 10}
            })
        return scenario_data

    # Remove apply_scenario_to_simulation from here; use the imported one instead


    def __init__(self, main_window):
        self.file_menu = None
        self.main_window = main_window
        self.create_menu()

    def create_menu(self):
        """Create file menu with save/load and scenario editor options"""
        menubar = self.main_window.menuBar()
        self.file_menu = menubar.addMenu('File')

        # Scenario Editor
        scenario_action = self.file_menu.addAction('Scenario Editor')
        scenario_action.triggered.connect(self.main_window.launch_scenario_editor)
        self.file_menu.addSeparator()

        self.QuickSave()
        self.QuickLoad()
        self.save_simulation()
        self.load_simulation()

    # Quick Save
    def QuickSave(self):
        """Quick save the current simulation state."""
        quick_save_action = self.file_menu.addAction('Quick Save')
        quick_save_action.setShortcut('F5')
        quick_save_action.triggered.connect(self.quick_save)

    def quick_save(self):
        # Use SaveLoadManager to quick save
        if hasattr(self.main_window, 'save_load_manager'):
            self.main_window.save_load_manager.quick_save()
        else:
            print("SaveLoadManager not available for quick save.")

    # Quick Load
    def QuickLoad(self):
        """Quick load the last saved simulation state."""
        quick_load_action = self.file_menu.addAction('Quick Load')
        quick_load_action.setShortcut('F9')
        quick_load_action.triggered.connect(self.quick_load)

    def quick_load(self):
        # Use SaveLoadManager to quick load
        if hasattr(self.main_window, 'save_load_manager'):
            self.main_window.save_load_manager.quick_load()
        else:
            print("SaveLoadManager not available for quick load.")


    
    
    # Save Simulation
    def save_simulation(self):
        """Save the current simulation state."""
        save_action = self.file_menu.addAction('Save Simulation')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_simulation_action)

    def save_simulation_action(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        filename, _ = QFileDialog.getSaveFileName(self.main_window, "Save Simulation", "", "Simulation Files (*.sim);;All Files (*)")
        if filename:
            if not filename.endswith('.sim'):
                filename += '.sim'
            try:
                scenario_data = self.export_current_simulation_as_scenario()
                with open(filename, 'w') as f:
                    import json
                    json.dump(scenario_data, f, indent=2)
                QMessageBox.information(self.main_window, "Success", f"Simulation saved: {filename}")
            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", f"Failed to save simulation: {str(e)}")

    
    # Load Simulation
    def load_simulation(self):
        """Load a previously saved simulation state."""
        load_action = self.file_menu.addAction('Load Simulation')
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_simulation_action)

    def load_simulation_action(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        filename, _ = QFileDialog.getOpenFileName(self.main_window, "Load Simulation", "saves/", "Scenario Files (*.scenario *.sim);;All Files (*)")
        if filename:
            try:
                with open(filename, 'r') as f:
                    import json
                    data = json.load(f)
                # Check format and handle appropriately
                if 'metadata' in data and 'items' in data:
                    scenario_data = data
                elif 'drones' in data and 'config' in data:
                    scenario_data = self.convert_sim_to_scenario(data)
                else:
                    scenario_data = data  # fallback
                apply_scenario_to_simulation(self.main_window, scenario_data)
                QMessageBox.information(self.main_window, "Success", f"Simulation loaded: {filename}")
            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", f"Failed to load simulation: {str(e)}")