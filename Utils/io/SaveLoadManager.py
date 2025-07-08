"""Save and load functionality for simulation data"""
import json
import pickle
import os
from datetime import datetime

class SaveLoadManager:
    """Manages saving and loading of simulation data"""
    
    def __init__(self):
        self.save_directory = "saves"
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """Ensure save directory exists"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def save_simulation(self, simulation_data, filename=None):
        """Save simulation data to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_{timestamp}.json"
        
        filepath = os.path.join(self.save_directory, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(simulation_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving simulation: {e}")
            return False
    
    def load_simulation(self, filename):
        """Load simulation data from file"""
        filepath = os.path.join(self.save_directory, filename)
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading simulation: {e}")
            return None
    
    def list_saves(self):
        """List all available save files"""
        if not os.path.exists(self.save_directory):
            return []
        
        saves = []
        for file in os.listdir(self.save_directory):
            if file.endswith('.json'):
                saves.append(file)
        return sorted(saves)