import numpy as np

class EscortFormationManager:
    @staticmethod
    def update_escort_formation(drones, target, get_target_position_func, escort_radius=80):
        """Update drone positions for escort formation around a VIP target."""
        if not target or not hasattr(target, 'is_vip'):
            return
        vip_position = get_target_position_func()
        for i, drone in enumerate(drones):
            if not drone.alive:
                continue
            angle = (2 * np.pi * i) / len(drones)
            escort_pos = vip_position + escort_radius * np.array([np.cos(angle), np.sin(angle)])
            to_escort_pos = escort_pos - drone.position
            distance = np.linalg.norm(to_escort_pos)
            if distance > 10:
                drone.velocity = (to_escort_pos / distance) * 2.0
            else:
                if hasattr(target, 'velocity'):
                    drone.velocity = target.velocity * 0.8
