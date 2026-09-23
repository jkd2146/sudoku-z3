# Sudoku Solver with Z3 (SMT)

A declarative Sudoku solver: instead of writing a search loop, the puzzle's
rules are stated as constraints and the [Z3](https://pypi.org/project/z3-solver/)
SMT solver finds an assignment that satisfies them.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python sudoku_z3.py
python sudoku_z3.py "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4.."
```

Blanks can be written as `.` or `0`.

## Core logic

```python
X = [[Int(f"x_{r}_{c}") for c in range(9)] for r in range(9)]

cells  = [And(1 <= X[r][c], X[r][c] <= 9) for r in range(9) for c in range(9)]
rows   = [Distinct(X[r]) for r in range(9)]
cols   = [Distinct([X[r][c] for r in range(9)]) for c in range(9)]
boxes  = [Distinct([X[3 * br + r][3 * bc + c] for r in range(3) for c in range(3)])
          for br in range(3) for bc in range(3)]
givens = [X[r][c] == grid[r][c] for r in range(9) for c in range(9) if grid[r][c]]

s = Solver()
s.add(cells + rows + cols + boxes + givens)
if s.check() == sat:
    m = s.model()
```

Each cell is an integer variable in 1–9; every row, column and 3×3 box must be
`Distinct`; the given clues are fixed. `s.check()` returns `sat` and the model
holds the solved grid (or `unsat` if the puzzle has no solution).
