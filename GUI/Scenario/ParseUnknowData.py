def parse_unknown_format(self, data):
    """Try to parse unknown file format"""
    scenario_data = {
        'metadata': {
            'name': 'Unknown Format Conversion',
            'mission_type': 'search_and_destroy',
            'difficulty': 'Normal',
            'time_limit': 300,
            'map_width': 1080,
            'map_height': 720,
            'grid_size': 20
        },
        'items': []
    }
    
    # Look for common keys and convert
    if 'drones' in data:
        for drone in data['drones']:
            scenario_data['items'].append({
                'type': 'drone',
                'position': drone.get('position', [100, 100]),
                'properties': {
                    'drone_id': drone.get('drone_id', 0),
                    'max_missiles': drone.get('max_missiles', 2),
                    'formation_role': 'assault'
                }
            })
    
    if 'targets' in data:
        for target in data['targets']:
            scenario_data['items'].append({
                'type': 'target',
                'position': target.get('position', [500, 500]),
                'properties': {
                    'target_type': target.get('target_type', 'standard'),
                    'health': target.get('health', 100),
                    'hidden': target.get('hidden', False)
                }
            })
    
    # Try different obstacle formats
    if 'obstacles' in data:
        print(f"Found obstacles in data: {data['obstacles']}")
        for i, obs in enumerate(data['obstacles']):
            print(f"Processing obstacle {i}: {obs}")
            
            # Handle different obstacle formats
            if isinstance(obs, dict):
                # Dictionary format
                pos = obs.get('position', [300 + i*60, 300])
                size = obs.get('size', 40)
            elif isinstance(obs, list) and len(obs) >= 2:
                # List format [x, y] or [x, y, size]
                pos = [obs[0], obs[1]]
                size = obs[2] if len(obs) > 2 else 40
            else:
                # Unknown format - create default
                pos = [300 + i*60, 300]
                size = 40
            
            scenario_data['items'].append({
                'type': 'obstacle',
                'position': pos,
                'properties': {
                    'size': size,
                    'destructible': False
                }
            })
            print(f"Added obstacle at {pos} with size {size}")
    
    if 'bases' in data:
        for base in data['bases']:
            scenario_data['items'].append({
                'type': 'base',
                'position': base.get('position', [50, 50]),
                'properties': {
                    'capacity': base.get('capacity', 10)
                }
            })
    
    return scenario_data