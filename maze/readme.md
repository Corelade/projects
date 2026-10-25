# Maze Solver

A Python maze solver that finds a path from a starting point (`A`) to an endpoint (`B`) using either **Breadth-First Search (BFS)** or **Depth-First Search (DFS)**.

## Search Algorithms

- **Breadth-First Search (BFS):** Uses `QueueFrontier` to explore paths level by level and find the shortest path.
- **Depth-First Search (DFS):** Uses `StackFrontier` to explore one path as far as possible before backtracking.

You can switch between the algorithms by updating the `self.frontier` attribute in the `Maze` class.

## Installation

1. Create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:

   **macOS/Linux**
   ```bash
   source venv/bin/activate
   ```

   **Windows**
   ```bash
   venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the solver by providing the path to a maze file:

```bash
python3 maze.py path_to_maze_file
```

For example:

```bash
python3 maze.py maze1.txt
```

## Maze Format

Maze files use the following characters:

- `A` — Starting point
- `B` — Goal
- `#` — Wall
- Space — Walkable path

The solver searches for a path from `A` to `B` and displays the solution if one exists.