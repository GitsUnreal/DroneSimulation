import json
import os
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class SaveLoadManager:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        
        # Set default save directory
        self.default_save_dir = os.path.join(os.getcwd(), "saves")
        self.ensure_save_directory()
        
    def ensure_save_directory(self):
        """Create saves directory if it doesn't exist"""
        if not os.path.exists(self.default_save_dir):
            os.makedirs(self.default_save_dir)
            print(f"Created saves directory: {self.default_save_dir}")
        
    def save_simulation(self, filename=None):
        """Save complete simulation state in scenario format"""
        if not filename:
            # Set default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"simulation_{timestamp}.scenario"  # Use .scenario extension
            default_path = os.path.join(self.default_save_dir, default_filename)
            
            filename, _ = QFileDialog.getSaveFileName(
                None, 
                "Save Simulation", 
                default_path,
                "Scenario Files (*.scenario);;All Files (*)"  # Use scenario format
            )
            if not filename:
                return False
        else:
            # For quick save, use the saves directory
            if not os.path.isabs(filename):
                filename = os.path.join(self.default_save_dir, filename)
                
        try:
            # Convert to scenario format
            scenario_data = {
                'metadata': {
                    'name': f"Simulation Save {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    'mission_type': 'search_and_destroy',  # Default
                    'difficulty': 'Normal',
                    'time_limit': 300,
                    'map_width': 1080,
                    'map_height': 720,
                    'grid_size': 20,
                    'saved_at': datetime.now().isoformat(),
                    'version': '1.0'
                },
                'items': []
            }
            
            # Add drones
            for i, drone in enumerate(self.main_controller.drones):
                scenario_data['items'].append({
                    'type': 'drone',
                    'position': [int(drone.position[0]), int(drone.position[1])],
                    'properties': {
                        'drone_id': i,
                        'max_missiles': getattr(drone, 'max_missiles', 2),
                        'formation_role': 'assault'
                    }
                })
            
            # Add target (assuming single target for now)
            if hasattr(self.main_controller, 'target') and self.main_controller.target:
                target = self.main_controller.target
                scenario_data['items'].append({
                    'type': 'target',
                    'position': [int(target.position[0]), int(target.position[1])],
                    'properties': {
                        'target_type': 'standard',
                        'health': getattr(target, 'health', 100),
                        'hidden': getattr(target, 'hidden', False)
                    }
                })
            
            # Add obstacles
            for obstacle in self.main_controller.obstacles:
                scenario_data['items'].append({
                    'type': 'obstacle',
                    'position': [int(obstacle.x), int(obstacle.y)],
                    'properties': {
                        'size': getattr(obstacle, 'size', 40),
                        'destructible': False
                    }
                })
            
            # Add base
            if hasattr(self.main_controller, 'base'):
                base = self.main_controller.base
                scenario_data['items'].append({
                    'type': 'base',
                    'position': [int(base.x()), int(base.y())],
                    'properties': {
                        'capacity': 10
                    }
                })
            
            with open(filename, 'w') as f:
                json.dump(scenario_data, f, indent=2)
                
            QMessageBox.information(None, "Success", f"Simulation saved to {filename}")
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save simulation: {str(e)}")
            return False

    def load_simulation(self, filename=None):
        """Load simulation from scenario format"""
        if not filename:
            filename, _ = QFileDialog.getOpenFileName(
                None, 
                "Load Simulation", 
                self.default_save_dir,
                "Scenario Files (*.scenario);;All Files (*)"  # Use scenario format
            )
            if not filename:
                return False
        else:
            if not os.path.isabs(filename):
                filename = os.path.join(self.default_save_dir, filename)
            
        if not os.path.exists(filename):
            QMessageBox.warning(None, "File Not Found", f"File {filename} does not exist")
            return False
            
        try:
            with open(filename, 'r') as f:
                scenario_data = json.load(f)
        
            # This will be handled by the MainWindow's apply_scenario_to_simulation method
            # For now, just show what would be loaded
            metadata = scenario_data.get('metadata', {})
            items = scenario_data.get('items', [])
            
            drone_count = len([item for item in items if item['type'] == 'drone'])
            target_count = len([item for item in items if item['type'] == 'target'])
            
            QMessageBox.information(None, "Load Info", 
                f"Loaded scenario: {metadata.get('name', 'Unknown')}\n"
                f"Drones: {drone_count}, Targets: {target_count}")
            
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load simulation: {str(e)}")
            return False

    def get_save_files(self):
        """Get list of available save files"""
        save_files = []
        if os.path.exists(self.default_save_dir):
            for file in os.listdir(self.default_save_dir):
                if file.endswith('.scenario'):  # Look for .scenario files
                    save_files.append(file)
        return sorted(save_files, reverse=True)  # Most recent first

    def delete_save_file(self, filename):
        """Delete a save file"""
        filepath = os.path.join(self.default_save_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    # Add the missing serialization methods
    def serialize_config(self):
        """Serialize simulation configuration"""
        return {
            'grid_size': 100,  # Default values since we don't have access to these
            'mode': 'normal',
            'simulation_speed': getattr(self.main_controller, 'simulation_speed', 1.0)
        }
        
    def serialize_drones(self):
        """Serialize drone states"""
        return [
            {
                'id': drone.drone_id,
                'position': [drone.position[0], drone.position[1]],
                'velocity': [drone.velocity[0], drone.velocity[1]],
                'health': getattr(drone, 'health', 100),
                'fuel': getattr(drone, 'fuel', 100),
                'alive': getattr(drone, 'alive', True),
                'missiles_fired': getattr(drone, 'missiles_fired', 0)
            }
            for drone in self.main_controller.drones
        ]
        
    def serialize_obstacles(self):
        """Serialize obstacle data"""
        return [
            {
                'position': [obstacle.x(), obstacle.y()],
                'width': obstacle.width(),
                'height': obstacle.height()
            }
            for obstacle in self.main_controller.obstacles
        ]
        
    def serialize_targets(self):
        """Serialize target data"""
        if self.main_controller.target:
            return {
                'position': [self.main_controller.target.x(), self.main_controller.target.y()],
                'alive': not getattr(self.main_controller.target, 'destroyed', False)
            }
        return None
        
    def serialize_simulation_state(self):
        """Serialize general simulation state"""
        return {
            'simulation_time': 0,  # You can track this if needed
            'target_destroyed': getattr(self.main_controller.target, 'destroyed', False)
        }