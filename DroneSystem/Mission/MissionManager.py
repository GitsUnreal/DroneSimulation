class MissionManager:
    """Handles mission objectives, win/loss conditions, and scenario logic."""
    def __init__(self):
        self.current_mission = None

    def set_mission(self, mission):
        self.current_mission = mission

    def check_mission_complete(self, drones, target):
        # Example: all drones landed and target destroyed
        all_landed = all(getattr(d, 'has_landed', False) for d in drones)
        target_destroyed = getattr(target, 'is_destroyed', lambda: False)()
        return all_landed and target_destroyed
