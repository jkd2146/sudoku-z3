"""Sudoku solver using the Z3 SMT solver.

Usage:
    python sudoku_z3.py                  # solves the built-in example
    python sudoku_z3.py "<81 chars>"     # digits 1-9, and 0 or . for blanks
"""
import sys

from z3 import And, Distinct, Int, Solver, sat

EXAMPLE = (
    "53..7...."
    "6..195..."
    ".98....6."
    "8...6...3"
    "4..8.3..1"
    "7...2...6"
    ".6....28."
    "...419..5"
    "....8..79"
)


def parse(puzzle: str) -> list[list[int]]:
    cells = [0 if c in ".0" else int(c) for c in puzzle if c in ".0123456789"]
    if len(cells) != 81:
        raise ValueError(f"expected 81 cells, got {len(cells)}")
    return [cells[r * 9:(r + 1) * 9] for r in range(9)]


def solve(grid: list[list[int]]) -> list[list[int]] | None:
    # --- core logic: declare the rules, let the solver find the model ---
    X = [[Int(f"x_{r}_{c}") for c in range(9)] for r in range(9)]

    cells  = [And(1 <= X[r][c], X[r][c] <= 9) for r in range(9) for c in range(9)]
    rows   = [Distinct(X[r]) for r in range(9)]
    cols   = [Distinct([X[r][c] for r in range(9)]) for c in range(9)]
    boxes  = [Distinct([X[3 * br + r][3 * bc + c] for r in range(3) for c in range(3)])
              for br in range(3) for bc in range(3)]
    givens = [X[r][c] == grid[r][c] for r in range(9) for c in range(9) if grid[r][c]]

    s = Solver()
    s.add(cells + rows + cols + boxes + givens)
    if s.check() != sat:
        return None
    m = s.model()
    return [[m.evaluate(X[r][c]).as_long() for c in range(9)] for r in range(9)]
    # --- end core logic ---


def fmt(grid: list[list[int]]) -> str:
    lines = []
    for r, row in enumerate(grid):
        if r and r % 3 == 0:
            lines.append("------+-------+------")
        chunks = [" ".join(str(v or ".") for v in row[i:i + 3]) for i in (0, 3, 6)]
        lines.append(" | ".join(chunks))
    return "\n".join(lines)


def is_valid(grid: list[list[int]]) -> bool:
    full = set(range(1, 10))
    rows = all(set(row) == full for row in grid)
    cols = all({grid[r][c] for r in range(9)} == full for c in range(9))
    boxes = all({grid[3 * br + r][3 * bc + c] for r in range(3) for c in range(3)} == full
                for br in range(3) for bc in range(3))
    return rows and cols and boxes


if __name__ == "__main__":
    puzzle = parse(sys.argv[1] if len(sys.argv) > 1 else EXAMPLE)
    print("Puzzle:\n" + fmt(puzzle) + "\n")
    solution = solve(puzzle)
    if solution is None:
        print("No solution.")
        sys.exit(1)
    print("Solution:\n" + fmt(solution))
    print("\nValid:", is_valid(solution))
