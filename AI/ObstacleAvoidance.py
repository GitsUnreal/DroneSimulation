class OAI:
    def __init__(self, drone, obstacles):
        """
        Initialize the OAI with a drone and a list of obstacles.
        :param drone: The drone object that will be controlled.
        :param obstacles: List of obstacle objects that the drone needs to avoid.
        """
        self.drone = drone
        self.obstacles = obstacles

    def make_grid(self):
        """
        Create a grid of points representing the environment.
        Each point is spaced by a fixed cell size and marked as blocked if it overlaps with any
        obstacle.
        Returns a dictionary where keys are (x, y) tuples and values are dictionaries with
        'pos' (the position), 'blocked' (boolean indicating if the point is blocked
        by an obstacle), and 'neighbors' (list of neighboring points).
        """
        grid = {}
        width = 1080
        height = 720
        cell_size = 10

        # Create a grid of points spaced by cell_size
        for y in range(0, height, cell_size):
            for x in range(0, width, cell_size):
                blocked = any(obs.contains(x, y) for obs in self.obstacles)
                grid[(x, y)] = {'pos': (x, y), 'blocked': blocked, 'neighbors': []}
        
        return grid
    
    def add_neighbors(self, grid, cell_size=20):
        """
        Add neighboring points to each point in the grid.
        Each point will have a list of neighboring points that are not blocked.
        :param grid: The grid dictionary created by make_grid.
        :param cell_size: The size of each cell in the grid.
        """
        directions = [
            (0, -cell_size),  # Up
            (cell_size, 0),   # Right
            (0, cell_size),   # Down
            (-cell_size, 0)   # Left
        ]

        for (x, y), data in grid.items():
            for dx, dy in directions:
                neighbor = (x + dx, y + dy)
                if neighbor in grid and not grid[neighbor]['blocked']:
                    data['neighbors'].append(neighbor)

    def find_path(self, grid, start, goal):
        """
        Find the shortest path from start to goal using A* algorithm.
        :param grid: The grid dictionary created by make_grid.
        :param start: The starting position as a (x, y) tuple.
        :param goal: The goal position as a (x, y) tuple.
        :return: A list of positions representing the path from start to goal.
        """
        open_set = {start}
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            if current == goal:
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)
            for neighbor in grid[current]['neighbors']:
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    open_set.add(neighbor)

        return []

    def heuristic(self, pos1, pos2):
        """Manhattan distance heuristic for A* pathfinding"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def reconstruct_path(self, came_from, current):
        """Reconstruct the path from start to goal"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path[1:]  # Return path without the starting position
