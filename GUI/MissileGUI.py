import numpy as np
from AI.GuidingMissile import GuidingMissile

def update_missiles(drones):
    """Update missile positions and remove inactive missiles"""
    for drone in drones:
        if hasattr(drone, 'missiles'):
            active_missiles = []
            
            for missile in drone.missiles:
                if not missile['active']:
                    continue
                    
                # Move missile along its path
                if missile['path'] and missile['path_index'] < len(missile['path']):
                    # Get current target waypoint
                    target_waypoint = missile['path'][missile['path_index']]
                    current_pos = np.array(missile['position'])
                    target_pos = np.array(target_waypoint)
                    
                    # Calculate direction to waypoint
                    direction = target_pos - current_pos
                    distance_to_waypoint = np.linalg.norm(direction)
                    
                    if distance_to_waypoint < 5:  # Reached waypoint
                        missile['path_index'] += 1
                        if missile['path_index'] >= len(missile['path']):
                            # Reached final target
                            print(f"Missile reached target at {missile['target']}")
                            missile['active'] = False
                            continue
                    else:
                        # Move towards waypoint
                        direction = direction / distance_to_waypoint
                        missile['position'][0] += direction[0] * missile['speed']
                        missile['position'][1] += direction[1] * missile['speed']
                else:
                    # No path, move directly to target
                    current_pos = np.array(missile['position'])
                    target_pos = np.array(missile['target'])
                    direction = target_pos - current_pos
                    distance_to_target = np.linalg.norm(direction)
                    
                    if distance_to_target < 5:  # Reached target
                        print(f"Missile reached target at {missile['target']}")
                        missile['active'] = False
                        continue
                    else:
                        direction = direction / distance_to_target
                        missile['position'][0] += direction[0] * missile['speed']
                        missile['position'][1] += direction[1] * missile['speed']
                
                # Check if missile is out of bounds
                if (missile['position'][0] < 0 or missile['position'][0] > 1080 or
                    missile['position'][1] < 0 or missile['position'][1] > 720):
                    missile['active'] = False
                    continue
                
                # Keep active missiles
                active_missiles.append(missile)
            
            # Update drone's missile list with only active missiles
            drone.missiles = active_missiles