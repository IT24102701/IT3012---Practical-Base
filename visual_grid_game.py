# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A scalable grid environment for the IT3012 practical."""

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=2,
        custom_walls=None
    ):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]
        self.facing = 'Up'

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        # Generate food
        self.food_positions = set()

        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)

            if (
                pos_tuple != (0, 0)
                and pos_tuple not in self.walls
            ):
                self.food_positions.add(pos_tuple)

        # Generate opponents
        self.opponents = []

        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]

            if (
                tuple(op_pos) != (0, 0)
                and tuple(op_pos) not in self.walls
                and tuple(op_pos) not in self.food_positions
            ):
                self.opponents.append(op_pos)

        # Generate toxic traps
        self.toxic_traps = set()

        while len(self.toxic_traps) < 5:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            trap_pos = (tx, ty)

            if (
                trap_pos != (0, 0)
                and trap_pos not in self.walls
                and trap_pos not in self.food_positions
                and trap_pos not in {
                    tuple(op) for op in self.opponents
                }
            ):
                self.toxic_traps.add(trap_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        """Return only local sensory information."""

        x, y = self.agent_pos

        # Determine the cell immediately ahead
        if self.facing == 'Up':
            front_cell = (x, y + 1)

        elif self.facing == 'Down':
            front_cell = (x, y - 1)

        elif self.facing == 'Left':
            front_cell = (x - 1, y)

        else:
            front_cell = (x + 1, y)

        wall_ahead = (
            front_cell in self.walls
            or front_cell[0] < 0
            or front_cell[0] >= self.width
            or front_cell[1] < 0
            or front_cell[1] >= self.height
        )

        food_here = tuple(self.agent_pos) in self.food_positions

        return {
            'wall_ahead': wall_ahead,
            'food_here': food_here
        }

    def execute_action(self, action: str):
        """Execute an action and update the environment."""

        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == 'Up':
            self.facing = 'Up'
            new_pos[1] = min(
                self.height - 1,
                new_pos[1] + 1
            )

        elif action == 'Down':
            self.facing = 'Down'
            new_pos[1] = max(
                0,
                new_pos[1] - 1
            )

        elif action == 'Left':
            self.facing = 'Left'
            new_pos[0] = max(
                0,
                new_pos[0] - 1
            )

        elif action == 'Right':
            self.facing = 'Right'
            new_pos[0] = min(
                self.width - 1,
                new_pos[0] + 1
            )

        # Check wall collision
        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        current_pos = tuple(self.agent_pos)

        # Collect food
        if current_pos in self.food_positions:
            self.food_positions.remove(current_pos)
            self.score += 20

        # Toxic trap
        if current_pos in self.toxic_traps:
            self.score -= 15

        # Move opponents
        for op in self.opponents:

            move = random.choice(
                ['Up', 'Down', 'Left', 'Right', 'Stay']
            )

            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1

            elif move == 'Down' and op[1] > 0:
                op[1] -= 1

            elif move == 'Left' and op[0] > 0:
                op[0] -= 1

            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )


class SimpleReflexAgent:
    """
    Simple Reflex Agent using only condition-action rules.
    No internal history is stored.
    """

    def sense_and_act(self, percept):

        if percept['food_here']:
            return 'Stay'

        if percept['wall_ahead']:
            return 'Left'

        else:
            return 'Up'


class ModelBasedAgent:
    """
    Model-Based Agent with internal state and memory.
    """

    def __init__(self, width, height):

        self.width = width
        self.height = height

        # Internal state
        self.visited_cells = set()
        self.internal_pos = [0, 0]

        # Remember previous information
        self.last_percept = None
        self.last_action = None

    def sense_and_act(self, percept):

        # Store the current percept
        self.last_percept = percept

        # Current internal position
        current_pos = tuple(self.internal_pos)

        # Remember current cell
        self.visited_cells.add(current_pos)

        # Rule 1: collect food
        if percept['food_here']:
            self.last_action = 'Stay'
            return 'Stay'

        x, y = current_pos

        # Possible neighboring positions
        neighbours = {
            'Up': (x, y + 1),
            'Right': (x + 1, y),
            'Down': (x, y - 1),
            'Left': (x - 1, y)
        }

        # Keep only positions inside the grid
        valid_actions = {}

        for action, position in neighbours.items():

            nx, ny = position

            if (
                0 <= nx < self.width
                and 0 <= ny < self.height
            ):
                valid_actions[action] = position

        # Prefer unvisited positions
        for action in [
            'Up',
            'Right',
            'Down',
            'Left'
        ]:

            if action in valid_actions:

                next_position = valid_actions[action]

                if next_position not in self.visited_cells:

                    self.last_action = action

                    # Update internal model
                    self.internal_pos = [
                        next_position[0],
                        next_position[1]
                    ]

                    return action

        # If all available positions were visited,
        # choose any available direction.
        for action in [
            'Up',
            'Right',
            'Down',
            'Left'
        ]:

            if action in valid_actions:

                self.last_action = action

                next_position = valid_actions[action]

                self.internal_pos = [
                    next_position[0],
                    next_position[1]
                ]

                return action

        # Final fallback
        self.last_action = 'Stay'
        return 'Stay'


def run_simple_reflex_simulation():

    env = VisualGridHuntGame(
        width=12,
        height=12,
        num_food=15,
        num_opponents=0
    )

    agent = SimpleReflexAgent()

    for _ in range(60):

        if env.is_done():
            break

        percept = env.get_percept()
        action = agent.sense_and_act(percept)

        print(
            f"Percept: {percept} | "
            f"Action: {action}"
        )

        env.execute_action(action)

    print("\nSimple Reflex Simulation finished.")
    print(f"Final position: {env.agent_pos}")
    print(f"Final score: {env.score}")
    print(f"Steps: {env.steps}")


class GridGameGUI:
    """
    Tkinter visual interface for the Model-Based Agent.
    """

    def __init__(
        self,
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0,
        walls=None
    ):

        self.root = root

        self.root.title(
            "IT3012 - Model-Based Grid Hunt"
        )

        # Create environment
        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )

        # Create Model-Based Agent
        self.agent = ModelBasedAgent(
            width=width,
            height=height
        )

        # Canvas size
        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height
            )
        )

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(
            root,
            width=canvas_w,
            height=canvas_h,
            bg="white"
        )

        self.canvas.pack()

        # Information label
        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial", 14)
        )

        self.label.pack(pady=10)

        # Start button
        self.btn = tk.Button(
            root,
            text="Start Model-Based Simulation",
            command=self.run_loop,
            font=("Arial", 12),
            bg="#000066",
            fg="white"
        )

        self.btn.pack(pady=5)

        # Initial grid
        self.draw_grid()

    def draw_grid(self):

        self.canvas.delete("all")

        # Draw cells
        for x in range(self.env.width):

            for y in range(self.env.height):

                x1 = x * self.cell_size

                y1 = (
                    self.env.height - 1 - y
                ) * self.cell_size

                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if (x, y) in self.env.walls:
                    cell_color = "#64748b"
                else:
                    cell_color = "#f1f5f9"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=cell_color,
                    outline="#cbd5e1"
                )

                if (
                    self.cell_size >= 40
                    and (x, y) in self.env.walls
                ):

                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=("Arial", 8, "bold")
                    )

        # Draw food
        for fx, fy in self.env.food_positions:

            offset = self.cell_size * 0.25

            x1 = fx * self.cell_size + offset

            y1 = (
                (self.env.height - 1 - fy)
                * self.cell_size
                + offset
            )

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706"
            )

        # Draw opponents
        for ox, oy in self.env.opponents:

            offset = self.cell_size * 0.2

            x1 = ox * self.cell_size + offset

            y1 = (
                (self.env.height - 1 - oy)
                * self.cell_size
                + offset
            )

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000"
            )

        # Draw agent
        ax, ay = self.env.agent_pos

        offset = self.cell_size * 0.15

        x1 = ax * self.cell_size + offset

        y1 = (
            (self.env.height - 1 - ay)
            * self.cell_size
            + offset
        )

        self.canvas.create_oval(
            x1,
            y1,
            x1 + self.cell_size * 0.7,
            y1 + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a"
        )

        # Draw toxic traps
        for tx, ty in self.env.toxic_traps:

            cx = (
                tx * self.cell_size
                + self.cell_size / 2
            )

            cy = (
                (self.env.height - 1 - ty)
                * self.cell_size
                + self.cell_size / 2
            )

            r = self.cell_size * 0.3

            self.canvas.create_polygon(
                cx,
                cy - r,
                cx + r,
                cy,
                cx - r,
                cy,
                fill="#800080",
                outline="#4B0082"
            )

    def run_loop(self):

        self.btn.config(state="disabled")

        def step():

            if not self.env.is_done():

                # Get local percept
                percept = self.env.get_percept()

                # Ask Model-Based Agent for an action
                action = self.agent.sense_and_act(
                    percept
                )

                # Execute action
                self.env.execute_action(action)

                # Update visual display
                self.draw_grid()

                self.label.config(
                    text=(
                        f"Model-Based Agent | "
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Action: {action}"
                    )
                )

                # Continue after 250 milliseconds
                self.root.after(250, step)

            else:

                if self.env.collision:
                    end_text = (
                        f"Collision! Game Over! "
                        f"Final Score: {self.env.score}"
                    )
                else:
                    end_text = (
                        f"Finished! "
                        f"Final Score: {self.env.score}"
                    )

                self.label.config(text=end_text)

                self.btn.config(state="normal")

        step()


if __name__ == "__main__":

    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0
    )

    root.mainloop()