# agent.py

from collections import deque
import heapq
import random


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']

        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SearchAgent:
    """Agent that uses uninformed search algorithms."""

    def __init__(self):
        self.actions = ['Up', 'Down', 'Left', 'Right']

        # Step 1.3: Offline planning
        self.plan = []
        self.active_algo = 'BFS'

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
                current, walls, grid_size
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
                current, walls, grid_size
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
                current, walls, grid_size
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

    def sense_and_act(self, percept: dict) -> str:
        """Create an offline plan and execute it one action at a time."""

        # Create a new plan if the current plan is empty
        if not self.plan:

            start = tuple(percept['agent_pos'])
            food_positions = percept['all_food']

            walls = {
                tuple(wall)
                for wall in percept['walls']
            }

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

            # Run the selected search algorithm
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

            else:
                raise ValueError(
                    f"Unknown search algorithm: {self.active_algo}"
                )

        # Execute the first action from the plan
        if self.plan:
            return self.plan.pop(0)

        # No path found
        return 'Stay'