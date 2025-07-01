from typing import List, Dict, Optional
from .MissileSystem import Missile, MissileType, MissileConfig
from .ObstacleAvoidance import OAI

class MissileManager:
    def __init__(self, oai: OAI, grid: dict):
        self.missiles: List[Missile] = []
        self.oai = oai
        self.grid = grid
        self.missile_counter = 0
        self.explosion_effects: List[dict] = []
        self.target = None  # Add target reference

    def set_target(self, target):
        """Set the current target for missile tracking"""
        self.target = target

    def fire_missile(self, drone, target_pos: tuple, missile_type: MissileType = MissileType.STANDARD,
                    config: MissileConfig = None) -> bool:
        """Fire a missile from a drone"""
        if not drone.can_fire_missile():
            return False

        self.missile_counter += 1
        missile_id = f"missile_{self.missile_counter}"
        
        # Create missile with pathfinding
        missile = Missile(
            missile_id=missile_id,
            drone_id=drone.drone_id,
            missile_type=missile_type,
            start_pos=(drone.position[0], drone.position[1]),
            target_pos=target_pos,
            config=config or MissileConfig()
        )
        
        # Store target reference in missile
        if self.target:
            missile.target_object = self.target
        
        # Calculate path using existing pathfinding
        start_grid = self.oai.snap_to_grid(missile.position)
        goal_grid = self.oai.snap_to_grid(target_pos)
        path = self.oai.find_path(self.grid, start_grid, goal_grid, drone)
        
        if path:
            missile.path = path
        
        self.missiles.append(missile)
        drone.missiles_fired += 1
        
        print(f"Fired {missile_type.value} missile {missile_id} from drone {drone.drone_id} to {target_pos}")
        return True

    def reload_missiles(self, drone):
        """Reload missiles for a drone"""
        if hasattr(drone, 'max_missiles'):
            drone.missiles_fired = 0
            print(f"Drone {drone.drone_id} reloaded missiles")
        else:
            print(f"Drone {drone.drone_id} cannot reload missiles (no max_missiles attribute)")

    def update_missiles(self, dt: float, drones: List, obstacles: List):
        """Update all missiles"""
        active_missiles = []
        
        for missile in self.missiles:
            if missile.update(dt, drones, obstacles):
                active_missiles.append(missile)
            else:
                # Add explosion effect if needed
                explosion = missile.get_explosion_effect()
                if explosion['active']:
                    self.explosion_effects.append(explosion)
        
        self.missiles = active_missiles
        
        # Update explosion effects
        self.explosion_effects = [
            effect for effect in self.explosion_effects 
            if effect.get('intensity', 0) > 0.1
        ]

    def get_missiles_for_drone(self, drone_id: int) -> List[Missile]:
        """Get all missiles fired by a specific drone"""
        return [m for m in self.missiles if m.drone_id == drone_id]

    def get_active_missiles(self) -> List[Missile]:
        """Get all active missiles"""
        return self.missiles.copy()

    def clear_missiles_for_drone(self, drone_id: int):
        """Clear all missiles for a specific drone"""
        self.missiles = [m for m in self.missiles if m.drone_id != drone_id]

    def get_missile_stats(self) -> dict:
        """Get statistics about missiles"""
        total = len(self.missiles)
        by_type = {}
        by_state = {}
        
        for missile in self.missiles:
            missile_type = missile.missile_type.value
            by_type[missile_type] = by_type.get(missile_type, 0) + 1
            
            state = missile.state.value
            by_state[state] = by_state.get(state, 0) + 1
        
        return {
            'total_active': total,
            'by_type': by_type,
            'by_state': by_state,
            'explosion_effects': len(self.explosion_effects)
        }