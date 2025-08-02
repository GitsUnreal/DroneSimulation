import numpy as np

class MovementManager:
    @staticmethod
    def move_drone_towards_target(drone, target_pos, speed=2.0):
        """Move drone towards the target position"""
        if target_pos is None:
            return
        try:
            direction = target_pos - drone.position
            distance = np.linalg.norm(direction)
            if distance > 0:
                direction = direction / distance
                drone.velocity = direction * speed
        except Exception as e:
            print(f"Error in move_drone_towards_target: {e}")

    @staticmethod
    def move_drone_to_base(drone, base_pos, speed=2.0):
        """Move drone towards the base position"""
        if base_pos is None:
            return
        try:
            direction = base_pos - drone.position
            distance = np.linalg.norm(direction)
            if distance > 0:
                direction = direction / distance
                drone.velocity = direction * speed
        except Exception as e:
            print(f"Error in move_drone_to_base: {e}")

    @staticmethod
    def move_drone_in_search_pattern(drone, simulation_step, speed=1.5):
        """Move drone in a spiral search pattern"""
        try:
            if not hasattr(drone, 'search_center'):
                drone.search_center = drone.position.copy()
                drone.search_radius = 50
                drone.search_angle = 0
            drone.search_angle += 0.1
            drone.search_radius += 0.5
            search_x = drone.search_center[0] + drone.search_radius * np.cos(drone.search_angle)
            search_y = drone.search_center[1] + drone.search_radius * np.sin(drone.search_angle)
            search_pos = np.array([search_x, search_y])
            direction = search_pos - drone.position
            distance = np.linalg.norm(direction)
            if distance > 0:
                direction = direction / distance
                drone.velocity = direction * speed
            if drone.search_radius > 200:
                drone.search_radius = 50
                drone.search_angle = 0
        except Exception as e:
            print(f"Error in move_drone_in_search_pattern: {e}")
