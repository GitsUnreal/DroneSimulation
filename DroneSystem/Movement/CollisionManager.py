import numpy as np

class CollisionManager:
    @staticmethod
    def handle_drone_collisions(drones):
        for i, drone in enumerate(drones):
            for j, other in enumerate(drones):
                if i != j and other.alive and not (hasattr(other, 'has_landed') and other.has_landed):
                    dist = np.linalg.norm(drone.position - other.position)
                    if dist < 20:
                        direction = drone.position - other.position
                        if np.linalg.norm(direction) > 0:
                            direction /= np.linalg.norm(direction)
                            drone.position += direction * 2
                            other.position -= direction * 2
