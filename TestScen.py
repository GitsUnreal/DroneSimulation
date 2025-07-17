# Create a file called fix_test_sim.py in your project root:

import json

def fix_test_sim():
    """Fix the Test.sim file to have proper drone IDs and position formats"""
    
    try:
        # Read the current file
        with open('saves/Test.sim', 'r') as f:
            data = json.load(f)
        
        # Fix drone IDs to be sequential
        if 'drones' in data:
            for i, drone in enumerate(data['drones']):
                drone['drone_id'] = i  # Force sequential IDs
                
                # Ensure position is a proper array
                if 'position' in drone:
                    pos = drone['position']
                    if isinstance(pos, (int, float)):
                        drone['position'] = [pos, pos]
                    elif not isinstance(pos, list):
                        drone['position'] = [100, 120 + i * 40]  # Default positions
                    elif len(pos) < 2:
                        drone['position'] = pos + [100] * (2 - len(pos))
        
        # Convert to scenario format
        scenario_data = {
            'metadata': {
                'name': data['metadata'].get('mission_name', 'Fixed Test Scenario'),
                'mission_type': data['metadata'].get('mission_type', 'search_and_destroy'),
                'difficulty': 'Normal',
                'time_limit': 300,
                'map_width': data['config'].get('map_width', 1080),
                'map_height': data['config'].get('map_height', 720),
                'grid_size': data['config'].get('grid_size', 20)
            },
            'items': []
        }
        
        # Convert drones
        for drone in data.get('drones', []):
            scenario_data['items'].append({
                'type': 'drone',
                'position': drone['position'],
                'properties': {
                    'drone_id': drone['drone_id'],
                    'max_missiles': drone.get('max_missiles', 2),
                    'formation_role': drone.get('formation_role', 'assault')
                }
            })
        
        # Convert targets
        for target in data.get('targets', []):
            scenario_data['items'].append({
                'type': 'target',
                'position': target['position'],
                'properties': {
                    'target_type': target.get('target_type', 'standard'),
                    'health': target.get('health', 100),
                    'hidden': target.get('hidden', False)
                }
            })
        
        # Convert obstacles
        for obstacle in data.get('obstacles', []):
            scenario_data['items'].append({
                'type': 'obstacle',
                'position': obstacle['position'],
                'properties': {
                    'size': obstacle.get('size', 40),
                    'destructible': obstacle.get('destructible', False)
                }
            })
        
        # Convert bases
        for base in data.get('bases', []):
            scenario_data['items'].append({
                'type': 'base',
                'position': base['position'],
                'properties': {
                    'capacity': base.get('capacity', 10)
                }
            })
        
        # Save the fixed scenario
        with open('saves/Test_Fixed.scenario', 'w') as f:
            json.dump(scenario_data, f, indent=2)
        
        print("Fixed scenario saved as Test_Fixed.scenario")
        print(f"Created {len([item for item in scenario_data['items'] if item['type'] == 'drone'])} drones")
        
    except Exception as e:
        print(f"Error fixing file: {e}")

if __name__ == "__main__":
    fix_test_sim()