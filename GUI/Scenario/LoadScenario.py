from GUI.Scenario.ApplyScenario import apply_scenario_to_simulation

def load_scenario_from_file(filename: str):
    """Load a scenario from the scenario editor format"""
    try:
        import json
        with open(filename, 'r') as f:
            scenario_data = json.load(f)
        
        apply_scenario_to_simulation(scenario_data)
        return True
    except Exception as e:
        print(f"Failed to load scenario: {e}")
        return False