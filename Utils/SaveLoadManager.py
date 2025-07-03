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
        """Save complete simulation state"""
        if not filename:
            # Set default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"simulation_{timestamp}.sim"
            default_path = os.path.join(self.default_save_dir, default_filename)
            
            filename, _ = QFileDialog.getSaveFileName(
                None, 
                "Save Simulation", 
                default_path,  # Start in saves directory with default name
                "Simulation Files (*.sim);;All Files (*)"
            )
            if not filename:
                return False
        else:
            # For quick save, use the saves directory
            if not os.path.isabs(filename):
                filename = os.path.join(self.default_save_dir, filename)
                
        try:
            simulation_data = {
                'metadata': {
                    'version': '1.0',
                    'saved_at': datetime.now().isoformat(),
                    'drone_count': len(self.main_controller.drones)
                },
                'config': self.serialize_config(),
                'drones': self.serialize_drones(),
                'obstacles': self.serialize_obstacles(),
                'targets': self.serialize_targets(),
                'simulation_state': self.serialize_simulation_state()
            }
            
            with open(filename, 'w') as f:
                json.dump(simulation_data, f, indent=2)
                
            QMessageBox.information(None, "Success", f"Simulation saved to {filename}")
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save simulation: {str(e)}")
            return False
            
    def load_simulation(self, filename=None):
        """Load complete simulation state"""
        if not filename:
            filename, _ = QFileDialog.getOpenFileName(
                None, 
                "Load Simulation", 
                self.default_save_dir,  # Start in saves directory
                "Simulation Files (*.sim);;All Files (*)"
            )
            if not filename:
                return False
        else:
            # For quick load, use the saves directory
            if not os.path.isabs(filename):
                filename = os.path.join(self.default_save_dir, filename)
                
        if not os.path.exists(filename):
            QMessageBox.warning(None, "File Not Found", f"File {filename} does not exist")
            return False
                
        try:
            with open(filename, 'r') as f:
                simulation_data = json.load(f)
                
            # Validate version compatibility
            if simulation_data.get('metadata', {}).get('version') != '1.0':
                QMessageBox.warning(None, "Warning", "File version may be incompatible")
                
            # For now, just show what would be loaded
            drone_count = simulation_data.get('metadata', {}).get('drone_count', 0)
            saved_at = simulation_data.get('metadata', {}).get('saved_at', 'Unknown')
            QMessageBox.information(None, "Load Info", 
                f"Loaded simulation with {drone_count} drones\nSaved: {saved_at}")
            
            # TODO: Implement actual restoration logic
            # self.restore_drones(simulation_data['drones'])
            # self.restore_obstacles(simulation_data['obstacles'])
            # etc.
            
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load simulation: {str(e)}")
            return False

    def get_save_files(self):
        """Get list of available save files"""
        save_files = []
        if os.path.exists(self.default_save_dir):
            for file in os.listdir(self.default_save_dir):
                if file.endswith('.sim'):
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