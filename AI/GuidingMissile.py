from AI.ObstacleAvoidance import OAI

class GuidingMissile:
    """
    Handles missile pathfinding and obstacle avoidance using grid-based navigation.
    Each missile is created with a computed path and tracked by its drone.
    """

    def __init__(self, drone, target, oai: OAI, grid):
        """
        Initialize the guiding missile logic for a drone.
        
        :param drone: The drone launching the missile.
        :param target: The static or dynamic target position.
        :param oai: The obstacle avoidance interface (OAI).
        :param grid: The navigational grid for pathfinding.
        """
        self.drone = drone
        self.target = target
        self.oai = oai
        self.grid = grid

    def shoot_missile(self, start: tuple, goal: tuple, requesting_drone=None) -> bool:
        """
        Launch a missile from a given start to a goal position using obstacle avoidance.
        
        :param start: Starting (x, y) coordinates.
        :param goal: Target (x, y) coordinates.
        :param requesting_drone: Optional; used if pathfinding is relative to a specific drone.
        :return: True if the missile was successfully launched, else False.
        """
        if not self.drone.can_fire_missile():
            print(f"Drone {self.drone.drone_id}: Cannot fire missile - limit reached or destroyed.")
            return False

        # Snap to grid to ensure valid coordinates
        start_grid = self.oai.snap_to_grid(start)
        goal_grid = self.oai.snap_to_grid(goal)

        path = self.oai.find_path(self.grid, start_grid, goal_grid, requesting_drone)

        missile_data = {
            'position': [float(start[0]), float(start[1])],
            'target': goal,
            'path': path if path else [goal_grid],  # Fallback to direct path
            'path_index': 0,
            'active': True,
            'speed': 3.0,
            'missile_id': f"drone_{self.drone.drone_id}_missile_{self.drone.missiles_fired + 1}"
        }

        if not hasattr(self.drone, 'missiles'):
            self.drone.missiles = []

        self.drone.missiles.append(missile_data)

        print(f"Missile launched from {start} to {goal} with {len(missile_data['path'])} waypoints.")

        return True
