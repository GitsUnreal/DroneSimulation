import numpy as np

DESIRED_SEPARATION = 25
NEIGHBOR_RADIUS = 100
MAX_SPEED = 4.0

def distance(boid1, boid2):
    """
    Calculate the distance between two boids.
    :param boid1: First boid object.
    :param boid2: Second boid object.
    :return: Distance between the two boids.
    """
    return np.linalg.norm(np.array(boid1.position) - np.array(boid2.position))

class Boids:
    def __init__(self, drones):
        self.drones = drones

    def limit_speed(self, velocity):
        speed = np.linalg.norm(velocity)
        if speed > MAX_SPEED:
            return (velocity / speed) * MAX_SPEED
        else:
            return velocity

    def update(self):
        for drone in self.drones:
            sep = self.compute_separation(drone)
            ali = self.compute_alignment(drone)
            coh = self.compute_cohesion(drone)

            # Tune these weights as needed
            drone.velocity += 1.5 * sep + 1.0 * ali + 1.0 * coh
            drone.limit_speed()
            drone.position += drone.velocity

    def compute_separation(self, drone):
        steer = np.zeros(2)
        for other in self.drones:
            if other is not drone and distance(drone, other) < DESIRED_SEPARATION:
                steer += drone.position - other.position
        return steer
    
    def compute_alignment(self, drone):
        avg_vel = np.zeros(2)
        count = 0
        for other in self.drones:
            if other is not drone and distance(drone, other) < NEIGHBOR_RADIUS:
                avg_vel += other.velocity
                count += 1
        return (avg_vel / count - drone.velocity) if count > 0 else np.zeros(2)
    
    def compute_cohesion(self, drone):
        center_mass = np.zeros(2)
        count = 0
        for other in self.drones:
            if other is not drone and distance(drone, other) < NEIGHBOR_RADIUS:
                center_mass += other.position
                count += 1
        return (center_mass / count - drone.position) if count > 0 else np.zeros(2)

    def reset(self):
        """
        Reset the Boids behavior for all drones.
        This method can be used to reset the state of drones before starting a new simulation.
        """
        for drone in self.drones:
            drone.reset_boids_behavior()

    def get_positions(self):
        """
        Get the current positions of all drones.
        :return: A list of tuples representing the positions of each drone.
        """
        return [(drone.x, drone.y) for drone in self.drones if drone.alive]
    
    def get_velocities(self):
        """
        Get the current velocities of all drones.
        :return: A list of tuples representing the velocities of each drone.
        """
        return [(drone.velocity[0], drone.velocity[1]) for drone in self.drones if drone.alive]
    
    def get_boids_info(self):
        """
        Get detailed information about the drones.
        :return: A list of dictionaries containing position, velocity, and alive status of each drone.
        """
        return [{
            'position': (drone.x, drone.y),
            'velocity': (drone.velocity[0], drone.velocity[1]),
            'alive': drone.alive
        } for drone in self.drones]
    
    def get_boids_summary(self):
        """
        Get a summary of the Boids simulation.
        :return: A dictionary containing the count of alive and dead drones, and their positions and velocities.
        """
        return {
            'alive_count': self.get_boids_count(),
            'dead_count': self.get_dead_boids_count(),
            'positions': self.get_positions(),
            'velocities': self.get_velocities()
        }
    


