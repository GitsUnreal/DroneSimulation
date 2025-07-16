class Pathfinding:
    def __init__(self, oai):
        self.oai = oai
        self.grid = oai.make_grid()
        oai.add_neighbors(self.grid)
    
    def get_path_to_target(self, drone, goal_pos):
        """Get pathfinding route to a specific goal position"""
        start = self.oai.snap_to_grid(drone.position)
        goal = self.oai.snap_to_grid(goal_pos)
        return self.oai.find_path(self.grid, start, goal, drone)
    
    def update_grid(self):
        """Update pathfinding grid when obstacles change"""
        self.grid = self.oai.make_grid()
        self.oai.add_neighbors(self.grid)