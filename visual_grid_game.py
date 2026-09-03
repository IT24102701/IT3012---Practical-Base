# visual_grid_game.py

import random
import tkinter as tk

from agent import SearchAgent


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

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

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        # Dynamically generate random food positions
        # avoiding walls and the agent start
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

        # Generate adversarial opponents
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

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        """Return the environment information available to the agent."""

        return {
            'agent_pos': list(self.agent_pos),
            'opponent_positions': [
                list(op) for op in self.opponents
            ],
            'smells_food': tuple(self.agent_pos) in self.food_positions,
            'hit_wall': tuple(self.agent_pos) in self.walls,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions),

            # Step 1.1: Global state
            'grid_size': (self.width, self.height),
            'walls': list(self.walls),
            'all_food': list(self.food_positions)
        }

    def execute_action(self, action: str):
        """Execute one action in the environment."""

        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(
                self.height - 1,
                new_pos[1] + 1
            )

        elif action == 'Down':
            new_pos[1] = max(
                0,
                new_pos[1] - 1
            )

        elif action == 'Left':
            new_pos[0] = max(
                0,
                new_pos[0] - 1
            )

        elif action == 'Right':
            new_pos[0] = min(
                self.width - 1,
                new_pos[0] + 1
            )

        # Check wall collision
        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        # Check food
        tuple_pos = tuple(self.agent_pos)

        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        # Move opponents
        for op in self.opponents:
            move = random.choice([
                'Up',
                'Down',
                'Left',
                'Right',
                'Stay'
            ])

            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1

            elif move == 'Down' and op[1] > 0:
                op[1] -= 1

            elif move == 'Left' and op[0] > 0:
                op[0] -= 1

            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            # Check collision with the agent
            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        """Check whether the game has finished."""

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes."""

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=2,
        walls=None
    ):
        self.root = root
        self.root.title(
            "IT3012 - Scalable Multi-Agent Grid Hunt"
        )

        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )

        # Step 1.3: Create SearchAgent
        self.agent = SearchAgent()

        # Dynamically calculate cell size
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

        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial", 14)
        )
        self.label.pack(pady=10)

        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Arial", 12),
            bg="#000066",
            fg="white"
        )
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        """Draw the current state of the game."""

        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):

                x1 = x * self.cell_size
                y1 = (
                    self.env.height - 1 - y
                ) * self.cell_size

                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = (
                    "#f1f5f9"
                    if (x, y) not in self.env.walls
                    else "#64748b"
                )

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
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
                self.env.height - 1 - fy
            ) * self.cell_size + offset

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
                self.env.height - 1 - oy
            ) * self.cell_size + offset

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
            self.env.height - 1 - ay
        ) * self.cell_size + offset

        self.canvas.create_oval(
            x1,
            y1,
            x1 + self.cell_size * 0.7,
            y1 + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a"
        )

    def run_loop(self):
        """Run the search agent simulation."""

        self.btn.config(state="disabled")

        def step():

            if not self.env.is_done():

                # Get the current percept
                percept = self.env.get_percept()

                # Ask the SearchAgent for the next action
                action = self.agent.sense_and_act(percept)

                # Execute that action
                self.env.execute_action(action)

                self.draw_grid()

                self.label.config(
                    text=(
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Algorithm: {self.agent.active_algo} | "
                        f"Action: {action}"
                    )
                )

                self.root.after(250, step)

            else:

                if self.env.collision:
                    end_text = (
                        "Collision! Game Over! "
                        f"Final Score: {self.env.score}"
                    )
                else:
                    end_text = (
                        "Finished! "
                        f"Final Score: {self.env.score}"
                    )

                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()

    # Larger grid with 15 food and no opponents
    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0
    )

    root.mainloop()