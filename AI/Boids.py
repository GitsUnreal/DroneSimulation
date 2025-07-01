import numpy as np

# Behavior constants
DESIRED_SEPARATION = 30
NEIGHBOR_RADIUS = 100
MAX_SPEED = 4.0

def distance(boid1, boid2):
    """Calculate Euclidean distance between two boids."""
    return np.linalg.norm(np.array(boid1.position) - np.array(boid2.position))

class Boids:
    def __init__(self, drones):
        # Only include active drones (not landed ones)
        self.drones = [d for d in drones if d.alive and not (hasattr(d, 'has_landed') and d.has_landed)]

    def limit_speed(self, velocity):
        """Limit a velocity vector to MAX_SPEED."""
        speed = np.linalg.norm(velocity)
        return (velocity / speed) * MAX_SPEED if speed > MAX_SPEED else velocity

    def update(self):
        """Update all drones' velocities and positions based on Boids rules."""
        for drone in self.drones:
            sep = self.compute_separation(drone)
            ali = self.compute_alignment(drone)
            coh = self.compute_cohesion(drone)

            # Combine forces with tuned weights
            drone.velocity += 3.0 * sep + 0.5 * ali + 0.5 * coh
            drone.velocity = self.limit_speed(drone.velocity)
            drone.position += drone.velocity

    def compute_separation(self, drone):
        """Return a force vector to keep drone separated from nearby drones."""
        steer = np.zeros(2)
        count = 0

        for other in self.drones:
            # Skip landed drones
            if (other is not drone and 
                other.alive and 
                not (hasattr(other, 'has_landed') and other.has_landed)):
                dist = distance(drone, other)
                if 0 < dist < DESIRED_SEPARATION:
                    diff = (drone.position - other.position) / (dist ** 2)
                    steer += diff
                    count += 1

        if count > 0:
            steer /= count
            norm = np.linalg.norm(steer)
            if norm > 0:
                steer = (steer / norm) * MAX_SPEED - drone.velocity

        return steer

    def compute_alignment(self, drone):
        """Return a force vector to align with nearby drones' average velocity."""
        avg_vel = np.zeros(2)
        count = 0

        for other in self.drones:
            if (other is not drone and 
                other.alive and 
                not (hasattr(other, 'has_landed') and other.has_landed) and
                distance(drone, other) < NEIGHBOR_RADIUS):
                avg_vel += other.velocity
                count += 1

        return (avg_vel / count - drone.velocity) if count else np.zeros(2)

    def compute_cohesion(self, drone):
        """Return a force vector to steer drone toward the center of mass of neighbors."""
        center_mass = np.zeros(2)
        count = 0

        for other in self.drones:
            if (other is not drone and 
                other.alive and 
                not (hasattr(other, 'has_landed') and other.has_landed) and
                distance(drone, other) < NEIGHBOR_RADIUS):
                center_mass += other.position
                count += 1

        return (center_mass / count - drone.position) * 0.01 if count else np.zeros(2)

    def reset(self):
        """Reset each drone's Boids behavior (e.g. velocity, state)."""
        for drone in self.drones:
            drone.reset_boids_behavior()

    def get_positions(self):
        """Return list of positions for all alive drones."""
        return [tuple(drone.position) for drone in self.drones if drone.alive]

    def get_velocities(self):
        """Return list of velocities for all alive drones."""
        return [tuple(drone.velocity) for drone in self.drones if drone.alive]

    def get_boids_info(self):
        """Return detailed state of all drones."""
        return [{
            'position': tuple(drone.position),
            'velocity': tuple(drone.velocity),
            'alive': drone.alive
        } for drone in self.drones]

    def get_boids_summary(self):
        """Return summary including count and states of drones."""
        return {
            'alive_count': self.get_boids_count(),
            'dead_count': self.get_dead_boids_count(),
            'positions': self.get_positions(),
            'velocities': self.get_velocities()
        }

    def get_boids_count(self):
        return sum(1 for d in self.drones if d.alive)

    def get_dead_boids_count(self):
        return sum(1 for d in self.drones if not d.alive)
