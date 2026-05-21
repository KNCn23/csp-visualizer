"""Built-in CSP problem definitions: N-Queens, Map Coloring, Sudoku-4."""

from csp_solver import CSP


# ─── N-Queens ──────────────────────────────────────────────────────────────
def n_queens(n: int) -> CSP:
    variables = [f"Q{i}" for i in range(n)]
    domains   = {v: set(range(n)) for v in variables}
    neighbors = {v: set(variables) - {v} for v in variables}

    def constraint(xi, vi, xj, vj):
        i, j = int(xi[1:]), int(xj[1:])
        return vi != vj and abs(vi - vj) != abs(i - j)

    return CSP(variables, domains, neighbors, constraint)


# ─── Australia map coloring (classic AIMA example) ─────────────────────────
def australia_map() -> CSP:
    variables = ["WA", "NT", "SA", "Q", "NSW", "V", "T"]
    domains   = {v: {"red", "green", "blue"} for v in variables}
    edges = [("WA","NT"),("WA","SA"),("NT","SA"),("NT","Q"),
             ("SA","Q"),("SA","NSW"),("SA","V"),("Q","NSW"),("NSW","V")]
    neighbors = {v: set() for v in variables}
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)

    def constraint(xi, vi, xj, vj):
        return vi != vj

    return CSP(variables, domains, neighbors, constraint)


# ─── 4×4 Sudoku ────────────────────────────────────────────────────────────
def sudoku4(givens: dict | None = None) -> CSP:
    """4x4 Sudoku. `givens` is {(r,c): val} with 0-indexed coords."""
    givens = givens or {(0,0): 1, (1,2): 3, (3,1): 4}
    variables = [f"C{r}{c}" for r in range(4) for c in range(4)]
    domains = {}
    for r in range(4):
        for c in range(4):
            v = f"C{r}{c}"
            if (r, c) in givens:
                domains[v] = {givens[(r, c)]}
            else:
                domains[v] = {1, 2, 3, 4}

    neighbors = {v: set() for v in variables}
    def add(a, b):
        if a != b:
            neighbors[a].add(b); neighbors[b].add(a)

    for r in range(4):
        for c in range(4):
            v = f"C{r}{c}"
            for cc in range(4): add(v, f"C{r}{cc}")
            for rr in range(4): add(v, f"C{rr}{c}")
            br, bc = (r // 2) * 2, (c // 2) * 2
            for rr in range(br, br + 2):
                for cc in range(bc, bc + 2):
                    add(v, f"C{rr}{cc}")

    def constraint(xi, vi, xj, vj):
        return vi != vj

    return CSP(variables, domains, neighbors, constraint)
