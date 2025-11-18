import heapq
import math

def has_line_of_sight(grid, start, end):
    """Check if there's a direct line of sight between two points."""
    # Bresenham's line algorithm
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while x0 != x1 or y0 != y1:
        if not (0 <= x0 < len(grid[0]) and 0 <= y0 < len(grid)) or not grid[y0][x0]:
            return False
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return True

def smooth_path(grid, path):
    """Simplify path by removing unnecessary points with line-of-sight checks."""
    if len(path) < 3:
        return path
    
    smoothed_path = [path[0]]
    current_index = 0
    
    while current_index < len(path) - 1:
        next_index = len(path) - 1
        # Find farthest point with line of sight
        for test_index in range(current_index + 2, len(path)):
            if has_line_of_sight(grid, path[current_index], path[test_index]):
                next_index = test_index
        smoothed_path.append(path[next_index])
        current_index = next_index
    
    return smoothed_path

class Node:
    """A node in the grid for A* pathfinding"""
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # cost from start to current node
        self.h = 0  # heuristic cost from current node to goal
        self.f = 0  # total cost (g + h)

    def __lt__(self, other):
        return self.f < other.f

def astar(grid, start, goal):
    """
    Perform A* pathfinding on a grid.
    
    Args:
        grid: 2D list representing the grid (True for walkable, False for obstacle)
        start: tuple (x, y) for the starting grid position
        goal: tuple (x, y) for the goal grid position
    
    Returns:
        path: list of tuples (x, y) representing the path from start to goal (including both)
        If no path is found, returns an empty list.
    """
    # Check if start or goal is an obstacle
    if not grid[start[1]][start[0]] or not grid[goal[1]][goal[0]]:
        return []

    # Create start and goal nodes
    start_node = Node(start)
    goal_node = Node(goal)

    # Initialize open and closed sets
    open_set = []
    closed_set = set()

    # Add the start node to the open set
    heapq.heappush(open_set, start_node)

    # Define possible movement directions (8-way movement)
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    while open_set:
        # Pop the node with the lowest f score
        current_node = heapq.heappop(open_set)
        closed_set.add(current_node.position)

        # Check if we reached the goal
        if current_node.position == goal_node.position:
            path = []
            current = current_node
            while current:
                path.append(current.position)
                current = current.parent
            path = path[::-1]
            return smooth_path(grid, path)  # Smooth the path

        # Generate children
        for direction in directions:
            child_position = (current_node.position[0] + direction[0], 
                             current_node.position[1] + direction[1])

            # Check if the child is within the grid
            if (child_position[0] < 0 or child_position[0] >= len(grid[0]) or 
                child_position[1] < 0 or child_position[1] >= len(grid)):
                continue

            # Check if the child is walkable
            if not grid[child_position[1]][child_position[0]]:
                continue

            # Create child node
            child_node = Node(child_position, current_node)

            # Skip if child is in closed set
            if child_node.position in closed_set:
                continue

            # Calculate costs
            # Use sqrt(2) for diagonal moves
            move_cost = 1.0 if direction[0] == 0 or direction[1] == 0 else math.sqrt(2)
            child_node.g = current_node.g + move_cost
            # Euclidean distance for heuristic
            dx = child_node.position[0] - goal_node.position[0]
            dy = child_node.position[1] - goal_node.position[1]
            child_node.h = math.sqrt(dx*dx + dy*dy)
            child_node.f = child_node.g + child_node.h

            # Check if child is already in open set and if it's a better path
            found = False
            for open_node in open_set:
                if open_node.position == child_node.position and open_node.f <= child_node.f:
                    found = True
                    break
            if found:
                continue

            heapq.heappush(open_set, child_node)

    return []  # no path found
