import numpy as np

class PathfindingManager:
    @staticmethod
    def find_path(oai, grid, start_pos, goal_pos, drone):
        """Find a path from start_pos to goal_pos using the OAI's pathfinding."""
        start = oai.snap_to_grid(start_pos)
        goal = oai.snap_to_grid(goal_pos)
        return oai.find_path(grid, start, goal, drone)
