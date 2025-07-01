import numpy as np

def update_missiles(drones):
    """Update missile positions and remove inactive or out-of-bounds missiles."""
    for drone in drones:
        if not hasattr(drone, 'missiles') or not drone.missiles:
            continue  # Early exit for performance

        active_missiles = []

        for missile in drone.missiles:
            if not missile['active']:
                continue

            # Move missile using optimized logic
            if not _update_missile_position(missile):
                missile['active'] = False
                continue

            # Check bounds
            x, y = missile['position']
            if not (0 <= x <= 1080 and 0 <= y <= 720):
                missile['active'] = False
                continue

            active_missiles.append(missile)

        drone.missiles = active_missiles

def _update_missile_position(missile):
    """Update missile position and return False if target reached."""
    current_pos = np.array(missile['position'])

    # Determine next target: from path if available, else direct target
    if missile.get('path') and missile['path_index'] < len(missile['path']):
        target = np.array(missile['path'][missile['path_index']])
        reached_target = _move_towards(current_pos, target, missile)
        if reached_target:
            missile['path_index'] += 1
            if missile['path_index'] >= len(missile['path']):
                print(f"Missile reached target at {missile['target']}")
                return False
    else:
        target = np.array(missile['target'])
        reached_target = _move_towards(current_pos, target, missile)
        if reached_target:
            print(f"Missile reached target at {missile['target']}")
            return False
    
    return True

def _move_towards(current_pos, target_pos, missile, threshold=5):
    """Move missile toward target and return True if target is reached."""
    direction = target_pos - current_pos
    distance = np.linalg.norm(direction)

    if distance < threshold:
        return True

    unit_direction = direction / distance
    missile['position'][0] += unit_direction[0] * missile['speed']
    missile['position'][1] += unit_direction[1] * missile['speed']
    return False
