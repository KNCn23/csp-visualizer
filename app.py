"""Streamlit visualizer for CSP solver."""

import streamlit as st
import pandas as pd

from csp_solver import solve
from problems import n_queens, australia_map, sudoku4


st.set_page_config(page_title="CSP Visualizer", layout="wide")
st.title("CSP Visualizer")
st.caption("Backtracking · Arc Consistency · Forward Checking")

# ── Sidebar controls ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("Problem")
    problem_name = st.selectbox(
        "Choose a CSP",
        ["N-Queens", "Australia Map Coloring", "4x4 Sudoku"],
    )
    if problem_name == "N-Queens":
        n = st.slider("N", 4, 10, 6)
        csp = n_queens(n)
    elif problem_name == "Australia Map Coloring":
        csp = australia_map()
    else:
        csp = sudoku4()

    st.header("Algorithm")
    use_ac3 = st.checkbox("Run AC-3 pre-processing", True)
    use_fc  = st.checkbox("Forward checking during search", True)

    if st.button("Solve", type="primary"):
        solution, steps = solve(csp, use_ac3=use_ac3, use_fc=use_fc)
        st.session_state.solution = solution
        st.session_state.steps = steps
        st.session_state.step_idx = 0

# ── Main view ──────────────────────────────────────────────────────────────
if "steps" not in st.session_state:
    st.info("Configure a problem in the sidebar and click **Solve**.")
    st.stop()

steps = st.session_state.steps
solution = st.session_state.solution

c1, c2 = st.columns([2, 3])

with c1:
    st.subheader("Step navigator")
    st.write(f"Total steps: **{len(steps)}**")
    idx = st.slider("Step", 0, max(0, len(steps) - 1),
                    st.session_state.step_idx, key="step_idx")
    if idx < len(steps):
        step = steps[idx]
        st.markdown(f"**Step {idx + 1}** — `{step.kind}`")
        st.write(step.note)

        st.markdown("**Domains (current snapshot)**")
        rows = []
        for v, d in sorted(step.domains_snapshot.items()):
            rows.append({"Variable": v, "Domain": ", ".join(map(str, sorted(d, key=str)))})
        st.dataframe(pd.DataFrame(rows), hide_index=True, height=300)

        if step.assignment_snapshot:
            st.markdown("**Assignment so far**")
            st.json(step.assignment_snapshot)

with c2:
    st.subheader("Statistics")
    counts = {"assign": 0, "unassign": 0, "prune": 0, "ac3": 0}
    for s in steps:
        counts[s.kind] = counts.get(s.kind, 0) + 1
    st.dataframe(pd.DataFrame([
        {"Event": k, "Count": v} for k, v in counts.items()
    ]), hide_index=True)

    st.subheader("Solution")
    if solution:
        st.success(f"Solved with {len(solution)} variables assigned.")
        if problem_name == "N-Queens":
            n = len(solution)
            board = [["."] * n for _ in range(n)]
            for var, col in solution.items():
                row = int(var[1:])
                board[row][col] = "Q"
            st.code("\n".join(" ".join(r) for r in board))
        elif problem_name == "4x4 Sudoku":
            grid = [["."] * 4 for _ in range(4)]
            for v, val in solution.items():
                r, c = int(v[1]), int(v[2])
                grid[r][c] = str(val)
            st.code("\n".join(" ".join(r) for r in grid))
        else:
            st.json(solution)
    else:
        st.error("No solution found.")
