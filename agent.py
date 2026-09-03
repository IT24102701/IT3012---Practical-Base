# agent.py

from collections import deque
import heapq
import random
import math


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SearchAgent:
    """Agent that uses uninformed and informed search algorithms."""

    def __init__(self):
        self.actions = ['Up', 'Down', 'Left', 'Right']

        # Step 1.3: Offline planning
        self.plan = []

        # Use A* as the active search algorithm
        self.active_algo = 'AStar'


    def manhattan_distance(self, pos, goal):
        """Calculate Manhattan distance between two positions."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        """Calculate Euclidean distance between two positions."""
        return math.sqrt(
            (pos[0] - goal[0]) ** 2 +
            (pos[1] - goal[1]) ** 2
        )

    def get_neighbors(self, state, walls, grid_size):
        """Return valid neighboring states and their actions."""

        x, y = state
        width, height = grid_size

        neighbors = [
            ((x, y + 1), 'Up'),
            ((x, y - 1), 'Down'),
            ((x - 1, y), 'Left'),
            ((x + 1, y), 'Right')
        ]

        valid_neighbors = []

        for next_state, action in neighbors:
            nx, ny = next_state

            # Stay inside the grid
            if nx < 0 or nx >= width or ny < 0 or ny >= height:
                continue

            # Do not move through walls
            if next_state in walls:
                continue

            valid_neighbors.append((next_state, action))

        return valid_neighbors

    def bfs_search(self, start, goal, walls, grid_size):
        """Breadth-First Search using a FIFO queue."""

        frontier = deque([(start, [])])
        reached = {start}

        while frontier:
            current, path = frontier.popleft()

            if current == goal:
                return path

            for neighbor, action in self.get_neighbors(
                current,
                walls,
                grid_size
            ):
                if neighbor not in reached:
                    reached.add(neighbor)

                    new_path = path + [action]
                    frontier.append((neighbor, new_path))

        return []

    def dfs_search(self, start, goal, walls, grid_size):
        """Depth-First Search using a LIFO stack."""

        frontier = [(start, [])]
        reached = {start}

        while frontier:
            current, path = frontier.pop()

            if current == goal:
                return path

            for neighbor, action in self.get_neighbors(
                current,
                walls,
                grid_size
            ):
                if neighbor not in reached:
                    reached.add(neighbor)

                    new_path = path + [action]
                    frontier.append((neighbor, new_path))

        return []


    def ucs_search(self, start, goal, walls, grid_size):
        """Uniform-Cost Search using a priority queue."""

        frontier = [(0, start, [])]
        reached = {start: 0}

        while frontier:
            cost, current, path = heapq.heappop(frontier)

            if current == goal:
                return path

            for neighbor, action in self.get_neighbors(
                current,
                walls,
                grid_size
            ):
                new_cost = cost + 1

                if neighbor not in reached or new_cost < reached[neighbor]:
                    reached[neighbor] = new_cost

                    new_path = path + [action]

                    heapq.heappush(
                        frontier,
                        (new_cost, neighbor, new_path)
                    )

        return []


    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):
        """
        A* Search using:

            f(n) = g(n) + h(n)

        g(n): cost from the start node to the current node
        h(n): estimated cost from the current node to the goal
        f(n): estimated total cost
        """

        # Priority queue
        frontier = []

        # Set of explored states
        reached_states = set()

        # Calculate heuristic for the starting position
        if heuristic_type == 'manhattan':
            h_cost = self.manhattan_distance(
                start_pos,
                goal_pos
            )

        elif heuristic_type == 'euclidean':
            h_cost = self.euclidean_distance(
                start_pos,
                goal_pos
            )

        else:
            raise ValueError(
                f"Unknown heuristic type: {heuristic_type}"
            )

        # Starting node has g(n) = 0
        g_cost = 0

        # f(n) = g(n) + h(n)
        f_cost = g_cost + h_cost

        # A* priority queue tuple:
        # (f_cost, g_cost, current_pos, path_taken)
        heapq.heappush(
            frontier,
            (
                f_cost,
                g_cost,
                start_pos,
                []
            )
        )

        # Main A* loop
        while frontier:

            # Pop the node with the lowest f(n)
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(
                frontier
            )

            # Goal test
            if current_pos == goal_pos:
                return path_taken

            # Skip states that have already been explored
            if current_pos in reached_states:
                continue

            # Mark current state as explored
            reached_states.add(current_pos)

            # Expand neighboring states
            for neighbor, action in self.get_neighbors(
                current_pos,
                walls,
                grid_size
            ):
                # Ignore already explored states
                if neighbor in reached_states:
                    continue

                # Calculate g(new)
                new_g_cost = g_cost + 1

                # Calculate h(new)
                if heuristic_type == 'manhattan':
                    new_h_cost = self.manhattan_distance(
                        neighbor,
                        goal_pos
                    )
                else:
                    new_h_cost = self.euclidean_distance(
                        neighbor,
                        goal_pos
                    )

                # Calculate f(new)
                new_f_cost = new_g_cost + new_h_cost

                # Create new path
                new_path = path_taken + [action]

                # Add node to priority queue
                heapq.heappush(
                    frontier,
                    (
                        new_f_cost,
                        new_g_cost,
                        neighbor,
                        new_path
                    )
                )

        # No path found
        return []


    def sense_and_act(self, percept: dict) -> str:
        """Create an offline plan and execute it one action at a time."""

        # Create a new plan if the current plan is empty
        if not self.plan:

            # Current agent position
            start = tuple(percept['agent_pos'])

            # Get all remaining food
            food_positions = percept['all_food']

            # Convert wall positions to tuples
            walls = {
                tuple(wall)
                for wall in percept['walls']
            }

            # Get grid size
            grid_size = percept['grid_size']

            # No food remaining
            if not food_positions:
                return 'Stay'

            # Find the closest food using Manhattan distance
            goal = min(
                food_positions,
                key=lambda food:
                    abs(food[0] - start[0]) +
                    abs(food[1] - start[1])
            )

            goal = tuple(goal)

            # Select the search algorithm
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(
                    start,
                    goal,
                    walls,
                    grid_size
                )

            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(
                    start,
                    goal,
                    walls,
                    grid_size
                )

            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(
                    start,
                    goal,
                    walls,
                    grid_size
                )

            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(
                    start_pos=start,
                    goal_pos=goal,
                    walls=walls,
                    grid_size=grid_size,
                    heuristic_type='manhattan'
                )

            else:
                raise ValueError(
                    f"Unknown search algorithm: {self.active_algo}"
                )

        # Execute the first action from the plan
        if self.plan:
            return self.plan.pop(0)

        # No path found
        return 'Stay'


if __name__ == "__main__":
    agent = SearchAgent()

    start = (0, 0)
    goal = (3, 4)

    print("Manhattan:", agent.manhattan_distance(start, goal))
    print("Euclidean:", agent.euclidean_distance(start, goal))