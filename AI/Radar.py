
class Radar:
    def __init__(self, drones, obstacles, target):
        self.drones = drones
        self.obstacles = obstacles
        self.target = target

    def detect_drones(self):
        detected_drones = []
        for drone in self.drones:
            if drone.is_active():
                detected_drones.append(drone)
        return detected_drones

    def detect_obstacles(self):
        return [obs for obs in self.obstacles if obs.is_active()]

    def detect_target(self):
        return self.target if self.target.is_active() else None