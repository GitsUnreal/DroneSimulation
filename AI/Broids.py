class Boids:
    def __init__(self, drones):
        self.drones = drones

    def update(self):
        for drone in self.drones:
            drone.update_boids_behavior(self.drones)

    def apply_boids_behavior(self):
        """
        Apply the Boids algorithm to update the positions of drones based on flocking behavior.
        This method will adjust each drone's velocity and position based on the positions and velocities
        of nearby drones.
        """
        for drone in self.drones:
            drone.apply_boids_behavior(self.drones)

    def update_boids_behavior(self):
        """
        Update the Boids behavior for all drones.
        This method will be called periodically to adjust the drones' positions and velocities
        based on the Boids algorithm.
        """
        self.apply_boids_behavior()
        for drone in self.drones:
            drone.move_to()

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
        return [(drone.vx, drone.vy) for drone in self.drones if drone.alive]
    
    def get_boids_info(self):
        """
        Get detailed information about the drones.
        :return: A list of dictionaries containing position, velocity, and alive status of each drone.
        """
        return [{
            'position': (drone.x, drone.y),
            'velocity': (drone.vx, drone.vy),
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
    


