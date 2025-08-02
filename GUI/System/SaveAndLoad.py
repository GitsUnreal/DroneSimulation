from GUI.Components.UIComponentManager import UIComponentManager
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
import json
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from datetime import datetime
import os
from GUI.Scenario.ApplyScenario import apply_scenario_to_simulation


class SaveAndLoad:
    def __init__(self, sim_manager, canvas):
        self.sim_manager = sim_manager
        self.canvas = canvas

    def save_simulation(self):
        """Save simulation with file dialog"""
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Simulation", "", "Simulation Files (*.sim);;All Files (*)")
        
        if filename:
            if not filename.endswith('.sim'):
                filename += '.sim'
            
            try:
                self.save_load_manager.save_simulation(filename)
                QMessageBox.information(self, "Success", f"Simulation saved: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save simulation: {str(e)}")

    def load_simulation(self):
        """Load simulation with file dialog"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Simulation", "saves/", 
            "Scenario Files (*.scenario *.sim);;All Files (*)")  # Support both formats
    
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                print(f"Loading file: {filename}")
                print(f"File structure keys: {list(data.keys())}")
                
                # Check format and handle appropriately
                if 'metadata' in data and 'items' in data:
                    # It's already scenario format
                    print("Detected scenario format")
                    scenario_data = data
                elif 'drones' in data and 'config' in data:
                    # It's a .sim file - convert to scenario format
                    print("Detected .sim format - converting...")
                    scenario_data = self.convert_sim_to_scenario(data)
                else:
                    # Try to detect format by content
                    print("Unknown format - attempting to parse...")
                    scenario_data = self.parse_unknown_format(data)
                
                # Apply the scenario to simulation
                apply_scenario_to_simulation(self, scenario_data)
                
                QMessageBox.information(self, "Success", f"Simulation loaded: {filename}")
                
            except Exception as e:
                print(f"Error loading file: {e}")
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Error", f"Failed to load simulation: {str(e)}")

    
    def quick_save(self):
        """Quick save using scenario format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quicksave_{timestamp}.scenario"
        self.save_load_manager.save_simulation(filename)

    def quick_load(self):
        """Quick load from most recent save"""
        saves_dir = "saves"
        if os.path.exists(saves_dir):
            scenario_files = [f for f in os.listdir(saves_dir) if f.endswith('.scenario')]
            if scenario_files:
                # Load most recent file
                latest_file = max(scenario_files, key=lambda f: os.path.getctime(os.path.join(saves_dir, f)))
                full_path = os.path.join(saves_dir, latest_file)
                
                try:
                    with open(full_path, 'r') as f:
                        scenario_data = json.load(f)
                    apply_scenario_to_simulation(self, scenario_data)
                    QMessageBox.information(self, "Success", f"Loaded: {latest_file}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load: {str(e)}")
            else:
                QMessageBox.warning(self, "No Saves", "No save files found")
        else:
            QMessageBox.warning(self, "No Saves", "Saves directory not found")