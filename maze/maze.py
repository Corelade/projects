from PIL import Image, ImageDraw
import sys

class QueueFrontier:
    "Framework for Breadth First Search (FIFO)"

    def __init__(self) -> None:
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def empty(self):
        return len(self.frontier) == 0

    def contains(self, node):
        return node in [n for n in self.frontier]

    def remove(self) -> "Node":
        if not self.frontier:
            raise Exception("No Solution")

        node = self.frontier[0]
        self.frontier = self.frontier[1:]

        return node


class StackFrontier(QueueFrontier):
    "Framework for Depth First Search (LIFO)"

    def remove(self) -> "Node":
        if not self.frontier:
            raise Exception("No Solution")

        node = self.frontier[-1]
        self.frontier = self.frontier[:-1]

        return node


class Node:
    # I can only determine Parent when solution has been found

    def __init__(
        self, position: tuple[int, int], parent=None, start=False, goal=False
    ) -> None:
        self.parent = parent
        self.start = start
        self.goal = goal
        self.position = position

    def get_neighbors(
        self,
        walls: list[tuple[int, int]],
        boundary: tuple[int, int],
        explored: set["Node"],
    ) -> set["Node"]:
        "Get all the neighbors of a node"

        "boundary is a tuple[height, width]"

        # TODO
        # - Neighbors currently includes invalid cells(walls), we might need to remove that

        neighbors = set()

        for vert in range(self.position[0] - 1, self.position[0] + 2):
            if vert < 0 or vert > boundary[0]:
                continue

            for horz in range(self.position[1] - 1, self.position[1] + 2):
                if horz < 0 or horz > boundary[1]:
                    continue

                if self.position == (self.position[0], horz):
                    continue

                node = Node(position=(self.position[0], horz), parent=self)
                # if (self.position[0], horz) not in walls:
                if node not in walls and node not in explored:
                    # neighbors.add((self.position[0], horz))
                    neighbors.add(node)

            if self.position == (vert, self.position[1]):
                continue

            node = Node(position=(vert, self.position[1]), parent=self)
            # if (vert, self.position[1]) not in walls:
            if node not in walls and node not in explored:
                # neighbors.add((vert, self.position[1]))
                neighbors.add(node)

        return neighbors

    def __repr__(self) -> str:
        return f"{self.position}"

    def __str__(self) -> str:
        return f"{self.position}"

    def __eq__(self, other_node: "Node") -> bool:
        return self.position == other_node.position

    def __hash__(self) -> int:
        return hash(self.position)


class Maze:
    def __init__(self, text_file) -> None:
        self.walls = set()
        self.start = None
        self.goal = None
        self.height = None
        self.width = None
        self.rows = None
        self.solution = None
        self.explored = set()
        self.frontier = StackFrontier()

        try:
            with open(text_file, "r") as file:
                rows = file.readlines()
                self.rows = [line.strip() for line in rows]

                # get the total width and height of the maze
                self.height = len(self.rows) - 1
                self.width = max(len(line) for line in self.rows) - 1
        except FileNotFoundError:
            raise Exception('Maze file does not exist')

        a_count = 0
        b_count = 0

        for h_idx in range(self.height + 1):
            for w_idx in range(self.width + 1):
                if self.rows[h_idx][w_idx] == "#":
                    self.walls.add(Node(position=(h_idx, w_idx)))
                elif self.rows[h_idx][w_idx] == "A":
                    a_count += 1
                    self.start = Node(position=(h_idx, w_idx), start=True)
                    self.frontier.add(self.start)
                elif self.rows[h_idx][w_idx] == "B":
                    b_count += 1
                    self.goal = Node(position=(h_idx, w_idx), goal=True)
                elif self.rows[h_idx][w_idx] == " ":
                    pass
                else:
                    raise Exception("Invalid Sequence in Maze")

        if a_count != 1:
            raise ValueError('Starting point can only be at one position')
        if b_count != 1:
            raise ValueError('One end point is required')
        
    def solve(self):
        "Start by identifying the walls"

        while True:
            # for _ in range(6):

            if self.frontier.empty():
                return self.solution

            # print('Frontier ->', self.frontier.frontier)

            node = self.frontier.remove()
            "once we take a node, add it to explored so it doesnt get redone"
            self.explored.add(node)

            # print('Removed Node ->', node)

            if node == self.goal:
                self.solution = [node]
                while node.parent is not None:
                    node = node.parent
                    self.solution.append(node)
                return self.solution

            node_neighbors = node.get_neighbors(
                walls=self.walls,
                boundary=(self.height, self.width),
                explored=self.explored,
            )

            for neighbor in node_neighbors:
                if (
                    not self.frontier.contains(neighbor)
                    and neighbor not in self.explored
                ):
                    # print(f"neighbor of {node}", neighbor.position)
                    self.frontier.add(neighbor)

        # for node in self.frontier.frontier:
        #     print(node.position)

    def draw_maze(self, use_solution: bool = False, show_explored: bool = False):
        "Converts maze from text form to PNG"

        CELL_SIZE = 50

        # draw the image
        im = Image.new(
            "RGB",
            (CELL_SIZE * (self.width + 1), CELL_SIZE * (self.height + 1)),
            "black",
        )
        draw = ImageDraw.Draw(im)

        x = 0
        y = 0

        for h_idx in range(self.height + 1):
            for w_idx in range(self.width + 1):
                if self.rows[h_idx][w_idx] == "#":
                    draw.rectangle(
                        [(x, y), (CELL_SIZE + x, CELL_SIZE + y)], fill="gray"
                    )
                elif self.rows[h_idx][w_idx] == "B":
                    draw.rectangle(
                        [(x, y), (CELL_SIZE + x, CELL_SIZE + y)], fill="cyan"
                    )
                elif self.rows[h_idx][w_idx] == "A":
                    draw.rectangle(
                        [(x, y), (CELL_SIZE + x, CELL_SIZE + y)], fill="blue"
                    )

                if show_explored:
                    if (h_idx, w_idx) in [
                        node.position
                        for node in self.explored
                        if node != self.goal and node != self.start
                    ]:
                        draw.rectangle(
                            [(x, y), (CELL_SIZE + x, CELL_SIZE + y)], fill="red"
                        )

                if self.solution and use_solution:
                    if (h_idx, w_idx) in [
                        node.position
                        for node in self.solution
                        if node != self.start and node != self.goal
                    ]:
                        draw.rectangle(
                            [(x, y), (CELL_SIZE + x, CELL_SIZE + y)], fill="green"
                        )

                x += CELL_SIZE
            x = 0
            y += CELL_SIZE
        im.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError('Maze is required to run program')
    maze_file = sys.argv[1]
    m = Maze(text_file=maze_file)
    solution = m.solve()
    m.draw_maze(use_solution=True, show_explored=True)
