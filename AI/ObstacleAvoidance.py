import copy

class OAI:
    """
    Obstacle Avoidance Interface (OAI) for grid-based A* pathfinding
    with dynamic obstacle handling via drone positions.
    """

    def __init__(self, drones, obstacles, cell_size=20):
        """
        Initialize the OAI with drones, obstacles, and cell size.
        
        :param drones: List of drone objects to avoid during pathfinding.
        :param obstacles: List of static obstacle objects with a `contains(x, y)` method.
        :param cell_size: Size of each grid cell in pixels.
        """
        self.drones = drones
        self.obstacles = obstacles
        self.cell_size = cell_size

    def make_grid(self):
        """
        Build a grid dictionary of points spaced by `cell_size`.
        """
        grid = {}
        width, height = 1080, 720

        for y in range(0, height, self.cell_size):
            for x in range(0, width, self.cell_size):
                blocked = any(obs.contains(x, y) for obs in self.obstacles)
                grid[(x, y)] = {'pos': (x, y), 'blocked': blocked, 'neighbors': []}
        
        return grid

    def add_neighbors(self, grid):
        """
        Populate each cell's 'neighbors' list with adjacent, unblocked cells.
        """
        directions = [
            (0, -self.cell_size),   # Up
            (self.cell_size, 0),    # Right
            (0, self.cell_size),    # Down
            (-self.cell_size, 0)    # Left
        ]

        for (x, y), data in grid.items():
            data['neighbors'].clear()  # Clear existing neighbors
            for dx, dy in directions:
                neighbor = (x + dx, y + dy)
                if neighbor in grid and not grid[neighbor]['blocked']:
                    data['neighbors'].append(neighbor)

    def find_path(self, grid, start, goal, requesting_drone=None):
        """
        Use A* algorithm with lightweight dynamic blocking instead of deep copy.
        """
        # Handle timeout reset for drones
        if requesting_drone:
            requesting_drone.current_path_timer = getattr(requesting_drone, 'current_path_timer', 0) + 1
            if requesting_drone.current_path_timer > 100:
                requesting_drone.current_path = []
                requesting_drone.current_waypoint_index = 0
                requesting_drone.current_path_timer = 0

        # Validate endpoints
        if start not in grid or goal not in grid:
            return []

        if grid[start]['blocked']:
            start = self.find_nearest_unblocked(grid, start)
        if grid[goal]['blocked']:
            goal = self.find_nearest_unblocked(grid, goal)
        if not start or not goal:
            return []

        # Get dynamic obstacles (much faster than deep copy)
        blocked_positions = self.get_dynamic_obstacles(requesting_drone)

        open_set = {start}
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            if current == goal:
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)
            
            # Check neighbors with dynamic blocking
            for neighbor in grid[current]['neighbors']:
                # Skip if dynamically blocked by other drones
                if neighbor in blocked_positions:
                    continue
                    
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    open_set.add(neighbor)

        return []

    def get_dynamic_obstacles(self, requesting_drone):
        """
        Get a set of positions blocked by other drones (lightweight operation).
        """
        blocked_positions = set()
        
        for drone in self.drones:
            # Skip requesting drone, destroyed drones, AND landed drones
            if (drone != requesting_drone and 
                drone.alive and 
                not (hasattr(drone, 'has_landed') and drone.has_landed)):
                pos = self.snap_to_grid(drone.position)
                blocked_positions.add(pos)
        
        return blocked_positions

    def find_nearest_unblocked(self, grid, pos):
        """
        Find the closest unblocked cell to a given blocked position.
        """
        min_dist = float('inf')
        nearest = None

        for (x, y), data in grid.items():
            if not data['blocked']:
                dist = self.heuristic(pos, (x, y))
                if dist < min_dist:
                    min_dist = dist
                    nearest = (x, y)

        return nearest

    def heuristic(self, pos1, pos2):
        """Manhattan distance heuristic for A*."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def reconstruct_path(self, came_from, current):
        """Rebuild the path backwards from goal to start."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path[1:]  # Exclude start cell

    def snap_to_grid(self, pos):
        """Align a pixel position to the nearest grid cell."""
        x = round(pos[0] / self.cell_size) * self.cell_size
        y = round(pos[1] / self.cell_size) * self.cell_size
        return (int(x), int(y))
