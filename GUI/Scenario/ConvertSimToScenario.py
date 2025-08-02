def convert_sim_to_scenario(self, sim_data):
    """Convert .sim file format to scenario format"""
    try:
        # Extract metadata and config
        metadata = sim_data.get('metadata', {})
        config = sim_data.get('config', {})
        
        # Create scenario format
        scenario_data = {
            'metadata': {
                'name': metadata.get('mission_name', 'Converted Simulation'),
                'mission_type': metadata.get('mission_type', 'search_and_destroy'),
                'difficulty': 'Normal',
                'time_limit': 300,
                'map_width': config.get('map_width', 1080),
                'map_height': config.get('map_height', 720),
                'grid_size': config.get('grid_size', 20)
            },
            'items': []
        }
        
        # Convert drones
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
        
        # Convert targets
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
        
        # Convert obstacles - FIXED TO HANDLE DIFFERENT FORMATS
        for obs_data in sim_data.get('obstacles', []):
            try:
                # Handle different obstacle data formats
                if isinstance(obs_data, dict):
                    # Dictionary format with position and properties
                    pos = obs_data.get('position', [400, 300])
                    size = obs_data.get('size', 40)
                    width = obs_data.get('width', size)
                    height = obs_data.get('height', size)
                elif isinstance(obs_data, (list, tuple)) and len(obs_data) >= 2:
                    # Array format [x, y] or [x, y, size]
                    pos = [obs_data[0], obs_data[1]]
                    size = obs_data[2] if len(obs_data) > 2 else 40
                    width = height = size
                else:
                    # Unknown format - create default
                    pos = [400 + len(scenario_data['items']) * 60, 300]
                    width = height = 40
                
                scenario_data['items'].append({
                    'type': 'obstacle',
                    'position': pos,
                    'properties': {
                        'size': max(width, height),  # Use larger dimension
                        'width': int(width),
                        'height': int(height),
                        'destructible': False
                    }
                })
                print(f"Converted obstacle: pos={pos}, size={width}x{height}")
                
            except Exception as e:
                print(f"Error converting obstacle: {e}")
                # Create a fallback obstacle
                fallback_obs = {
                    'type': 'obstacle',
                    'position': [400 + len(scenario_data['items']) * 60, 300],
                    'properties': {
                        'size': 40,
                        'width': 40,
                        'height': 40,
                        'destructible': False
                    }
                }
                scenario_data['items'].append(fallback_obs)
        
        # Convert bases - FIXED TO HANDLE BOTH SINGLE AND ARRAY FORMATS
        bases_data = sim_data.get('bases', [])
        if bases_data:
            # Handle both single base object and array of bases
            if isinstance(bases_data, dict):
                # Single base object
                base_pos = bases_data.get('position', [50, 50])
                capacity = bases_data.get('capacity', 10)
            elif isinstance(bases_data, list) and len(bases_data) > 0:
                # Array of bases - use first one
                first_base = bases_data[0]
                base_pos = first_base.get('position', [50, 50])
                capacity = first_base.get('capacity', 10)
            else:
                # Fallback
                base_pos = [50, 50]
                capacity = 10
            
            scenario_data['items'].append({
                'type': 'base',
                'position': base_pos,
                'properties': {
                    'capacity': capacity
                }
            })
            print(f"Converted base: pos={base_pos}, capacity={capacity}")
        else:
            # No base data found - create default
            scenario_data['items'].append({
                'type': 'base',
                'position': [50, 50],
                'properties': {
                    'capacity': 10
                }
            })
            print("No base data found - created default base")
        
        return scenario_data
    
    except Exception as e:
        print(f"Error converting sim to scenario: {e}")
        import traceback
        traceback.print_exc()
        return {}