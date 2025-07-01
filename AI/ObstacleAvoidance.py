class OAI:
    def __init__(self, drones, obstacles, cell_size=20):
        """
        Initialize the OAI with drones and a list of obstacles.
        :param drones: List of drone objects that will be controlled.
        :param obstacles: List of obstacle objects that the drones need to avoid.
        :param cell_size: Size of each grid cell for pathfinding
        """
        self.drones = drones
        self.obstacles = obstacles
        self.cell_size = cell_size

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

        # Create a grid of points spaced by cell_size
        for y in range(0, height, self.cell_size):
            for x in range(0, width, self.cell_size):
                blocked = any(obs.contains(x, y) for obs in self.obstacles)
                grid[(x, y)] = {'pos': (x, y), 'blocked': blocked, 'neighbors': []}
                # print(f"Grid point created at {(x, y)} - Blocked: {blocked}")
        
        return grid
    
    def add_neighbors(self, grid):
        """
        Add neighboring points to each point in the grid.
        Each point will have a list of neighboring points that are not blocked.
        :param grid: The grid dictionary created by make_grid.
        """
        directions = [
            (0, -self.cell_size),  # Up
            (self.cell_size, 0),   # Right
            (0, self.cell_size),   # Down
            (-self.cell_size, 0)   # Left
        ]

        for (x, y), data in grid.items():
            for dx, dy in directions:
                neighbor = (x + dx, y + dy)
                if neighbor in grid and not grid[neighbor]['blocked']:
                    data['neighbors'].append(neighbor)

    def find_path(self, grid, start, goal, requesting_drone=None):
        """
        Find the shortest path from start to goal using A* algorithm.
        :param grid: The grid dictionary created by make_grid.
        :param start: The starting position as a (x, y) tuple.
        :param goal: The goal position as a (x, y) tuple.
        :param requesting_drone: The drone requesting the path (for individual pathfinding)
        :return: A list of positions representing the path from start to goal.
        """
        
        # Add timeout logic for individual drones
        if requesting_drone:
            if hasattr(requesting_drone, 'current_path_timer'):
                requesting_drone.current_path_timer += 1
            else:
                requesting_drone.current_path_timer = 0

            # Reset path if it's taking too long
            if requesting_drone.current_path_timer > 100:
                requesting_drone.current_path = []
                requesting_drone.current_waypoint_index = 0
                requesting_drone.current_path_timer = 0
        
        # Make sure start and goal are in the grid
        if start not in grid or goal not in grid:
            # print(f"Start {start} or goal {goal} not in grid")
            return []
        
        # If start or goal is blocked, find nearest unblocked cell
        if grid[start]['blocked']:
            start = self.find_nearest_unblocked(grid, start)
        if grid[goal]['blocked']:
            goal = self.find_nearest_unblocked(grid, goal)
            
        if not start or not goal:
            return []

        # Create a dynamic grid that considers other drones as temporary obstacles
        dynamic_grid = self.create_dynamic_grid(grid, requesting_drone)

        open_set = {start}
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            if current == goal:
                path = self.reconstruct_path(came_from, current)
                return path

            open_set.remove(current)
            for neighbor in dynamic_grid[current]['neighbors']:
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    open_set.add(neighbor)

        # print("No individual path found")
        return []

    def create_dynamic_grid(self, base_grid, requesting_drone):
        """
        Create a dynamic grid that considers other drones as temporary obstacles
        :param base_grid: The base grid created by make_grid.
        :param requesting_drone: The drone requesting the path (for individual pathfinding)
        :return: A modified grid with other drones treated as obstacles.
        """
        import copy
        dynamic_grid = copy.deepcopy(base_grid)
        
        # Add other drones as temporary obstacles
        for drone in self.drones:
            if drone != requesting_drone and drone.alive:
                drone_grid_pos = self.snap_to_grid(drone.position)
                if drone_grid_pos in dynamic_grid:
                    dynamic_grid[drone_grid_pos]['blocked'] = True
                    # Remove this position from neighbors of adjacent cells
                    for (x, y), data in dynamic_grid.items():
                        if drone_grid_pos in data['neighbors']:
                            data['neighbors'].remove(drone_grid_pos)
        
        return dynamic_grid

    def find_nearest_unblocked(self, grid, pos):
        """
        Find the nearest unblocked cell to the given position
        :param grid: The grid dictionary created by make_grid.
        :param pos: The position as a (x, y) tuple.
        :return: The nearest unblocked cell as a (x, y) tuple.
        """
        min_distance = float('inf')
        nearest = None
        
        for (x, y), data in grid.items():
            if not data['blocked']:
                distance = self.heuristic(pos, (x, y))
                if distance < min_distance:
                    min_distance = distance
                    nearest = (x, y)
        
        return nearest

    def heuristic(self, pos1, pos2):
        """
        Manhattan distance heuristic for A* pathfinding
        :param pos1: The first position as a (x, y) tuple.
        :param pos2: The second position as a (x, y) tuple.
        :return: The Manhattan distance between pos1 and pos2.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def reconstruct_path(self, came_from, current):
        """
        Reconstruct the path from start to goal
        :param came_from: A dictionary mapping each position to its predecessor.
        :param current: The current position to start reconstructing from.
        :return: A list of positions representing the path from start to goal.
        """
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path[1:]  # Return path without the starting position

    def snap_to_grid(self, pos):
        """
        Snap position to grid coordinates
        :param pos: The position as a (x, y) tuple.
        :return: The snapped position as a (x, y) tuple.
        """
        x = int(round(pos[0] / self.cell_size) * self.cell_size)
        y = int(round(pos[1] / self.cell_size) * self.cell_size)
        return (x, y)
