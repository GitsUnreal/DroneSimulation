import numpy as np

class StateManager:
    @staticmethod
    def update_drone_state(drone, main_controller):
        # If drone is returning to base, check for landing
        if hasattr(drone, 'returning_to_base') and drone.returning_to_base:
            base_distance = main_controller.distance_to_base(drone)
            if base_distance < 30:
                # Land the drone
                drone.position = main_controller.get_base_position()
                drone.sync_from_position()
                drone.velocity = np.zeros(2)
                drone.current_path = []
                drone.current_waypoint_index = 0
                drone.land_at_base()
                drone.returning_to_base = False
                if hasattr(drone, 'missiles'):
                    drone.missiles.clear()
        # Example: handle return to base
        if drone.has_attacked and not hasattr(drone, 'returning_to_base'):
            drone.returning_to_base = True
            path = main_controller.get_path_to_target(drone, (main_controller.base.x(), main_controller.base.y()))
            drone.current_path = path or []
            drone.current_waypoint_index = 0
            drone.path_id = f"drone_{drone.drone_id}_base_path_{len(drone.current_path)}"
        # Add more state transitions as needed
