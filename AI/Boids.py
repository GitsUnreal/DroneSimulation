import numpy as np

DESIRED_SEPARATION = 60  # Increased from 25 to 40
NEIGHBOR_RADIUS = 100
MAX_SPEED = 4.0  # Reduced from 10 to 8 for better control

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
        self.drones = [d for d in drones if d.alive]

    def limit_speed(self, velocity):
        """
        Limit the speed of the drone's velocity to a maximum value.
        :param velocity: The current velocity vector of the drone.
        :return: The limited velocity vector.
        """
        speed = np.linalg.norm(velocity)
        if speed > MAX_SPEED:
            return (velocity / speed) * MAX_SPEED
        else:
            return velocity

    def update(self):
        """
        Update the positions of all drones based on Boids behavior.
        This method applies separation, alignment, and cohesion rules to each drone.
        """

        for drone in self.drones:
            sep = self.compute_separation(drone)
            ali = self.compute_alignment(drone)
            coh = self.compute_cohesion(drone)

            # Stronger separation, weaker alignment and cohesion
            drone.velocity += 3.0 * sep + 0.5 * ali + 0.5 * coh
            drone.velocity = self.limit_speed(drone.velocity)
            drone.position += drone.velocity

    def compute_separation(self, drone):
        """
        Compute the separation force for a drone to avoid crowding neighbors.
        :param drone: The drone object for which to compute separation.
        :return: A vector representing the separation force.
        """

        steer = np.zeros(2)
        count = 0
        for other in self.drones:
            if other is not drone and other.alive and drone.alive:
                dist = distance(drone, other)
                if dist < DESIRED_SEPARATION and dist > 0:
                    # Stronger repulsion when closer
                    diff = drone.position - other.position
                    diff = diff / dist  # Normalize and weight by distance
                    diff = diff / dist  # Weight inversely by distance again for stronger effect
                    steer += diff
                    count += 1
        
        if count > 0:
            steer = steer / count
            # Normalize and apply max separation force
            if np.linalg.norm(steer) > 0:
                steer = (steer / np.linalg.norm(steer)) * MAX_SPEED
                steer = steer - drone.velocity
        
        return steer
    
    def compute_alignment(self, drone):
        """
        Compute the alignment force for a drone to match the average velocity of nearby drones.
        :param drone: The drone object for which to compute alignment.
        :return: A vector representing the alignment force.
        """
        avg_vel = np.zeros(2)
        count = 0
        for other in self.drones:
            if other is not drone and other.alive and distance(drone, other) < NEIGHBOR_RADIUS:
                avg_vel += other.velocity
                count += 1
        return (avg_vel / count - drone.velocity) if count > 0 else np.zeros(2)
    
    def compute_cohesion(self, drone):
        """
        Compute the cohesion force for a drone to move towards the center of mass of nearby drones.
        :param drone: The drone object for which to compute cohesion.
        :return: A vector representing the cohesion force.
        """
        center_mass = np.zeros(2)
        count = 0
        for other in self.drones:
            if other is not drone and other.alive and distance(drone, other) < NEIGHBOR_RADIUS:
                center_mass += other.position
                count += 1
        return (center_mass / count - drone.position) * 0.01 if count > 0 else np.zeros(2)  # Weaker cohesion

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



