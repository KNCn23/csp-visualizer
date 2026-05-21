# CSP Visualizer

An interactive Streamlit application that exposes the inner workings of a constraint satisfaction solver — every assignment, every domain reduction, every backtrack is recorded and replayable step-by-step.

## What it visualizes

| Algorithm | Where |
|---|---|
| **Backtracking search** | Core depth-first assignment loop |
| **AC-3 arc consistency** | Optional pre-processing pass |
| **Forward checking** | Domain pruning after each assignment |
| **MRV heuristic** | Variable ordering by smallest remaining domain |

## Built-in problems

- **N-Queens** (4–10) — place N non-attacking queens
- **Australia Map Coloring** — the classic AIMA 7-region 3-color problem
- **4×4 Sudoku** — with editable givens

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`, pick a problem in the sidebar, toggle AC-3 / forward checking, and step through the search tree.

## Architecture

```
├── csp_solver.py   # Generic CSP, AC-3, backtracking + forward checking, step log
├── problems.py     # N-Queens, Australia map, 4x4 Sudoku as CSP instances
├── app.py          # Streamlit UI: step navigator, domain table, solution view
└── requirements.txt
```

Every algorithmic event is recorded as a `Step` with the full domain and assignment snapshot, so the visualization replays the search faithfully.

## Adding a new problem

Define a function returning a `CSP(variables, domains, neighbors, constraint)` and add it to the sidebar selectbox in `app.py`. The constraint callable has signature `(xi, vi, xj, vj) -> bool`.

## License

MIT
