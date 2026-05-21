"""
Generic CSP solver with backtracking, AC-3, and forward checking.
Designed to record every step so an external visualizer can replay them.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Set, Tuple, Any
from copy import deepcopy


@dataclass
class CSP:
    variables: List[str]
    domains:   Dict[str, Set[Any]]
    neighbors: Dict[str, Set[str]]
    constraint: Callable[[str, Any, str, Any], bool]


@dataclass
class Step:
    kind:     str               # "assign" | "unassign" | "prune" | "ac3"
    variable: str = ""
    value:    Any = None
    pruned:   List[Tuple[str, Any]] = field(default_factory=list)
    domains_snapshot: Dict[str, Set[Any]] = field(default_factory=dict)
    assignment_snapshot: Dict[str, Any] = field(default_factory=dict)
    note: str = ""


# ─── AC-3 ──────────────────────────────────────────────────────────────────
def ac3(csp: CSP,
        domains: Dict[str, Set[Any]],
        steps: List[Step]) -> bool:
    queue = [(xi, xj) for xi in csp.variables for xj in csp.neighbors[xi]]
    while queue:
        xi, xj = queue.pop(0)
        if revise(csp, domains, xi, xj, steps):
            if not domains[xi]:
                return False
            for xk in csp.neighbors[xi] - {xj}:
                queue.append((xk, xi))
    return True


def revise(csp, domains, xi, xj, steps) -> bool:
    revised = False
    pruned_vals = []
    for x in list(domains[xi]):
        if not any(csp.constraint(xi, x, xj, y) for y in domains[xj]):
            domains[xi].remove(x)
            pruned_vals.append(x)
            revised = True
    if revised:
        steps.append(Step(
            kind="ac3",
            variable=xi,
            pruned=[(xi, v) for v in pruned_vals],
            domains_snapshot=deepcopy(domains),
            note=f"AC-3: {xi} consistent w/ {xj} — pruned {pruned_vals}",
        ))
    return revised


# ─── Backtracking with optional forward checking ───────────────────────────
def backtrack(csp: CSP,
              assignment: Dict[str, Any],
              domains:    Dict[str, Set[Any]],
              steps:      List[Step],
              use_fc:     bool = True) -> Dict[str, Any] | None:

    if len(assignment) == len(csp.variables):
        return assignment

    # MRV: choose variable with smallest domain
    unassigned = [v for v in csp.variables if v not in assignment]
    var = min(unassigned, key=lambda v: len(domains[v]))

    for value in sorted(domains[var], key=str):
        if all(csp.constraint(var, value, other, assignment[other])
               for other in assignment if other in csp.neighbors[var]):
            assignment[var] = value
            steps.append(Step(
                kind="assign", variable=var, value=value,
                domains_snapshot=deepcopy(domains),
                assignment_snapshot=dict(assignment),
                note=f"Try {var} = {value}",
            ))

            saved = {v: set(domains[v]) for v in csp.variables}
            ok = True
            if use_fc:
                pruned_log = []
                for nb in csp.neighbors[var]:
                    if nb in assignment: continue
                    to_remove = {v for v in domains[nb]
                                 if not csp.constraint(nb, v, var, value)}
                    if to_remove:
                        domains[nb] -= to_remove
                        pruned_log.extend((nb, v) for v in to_remove)
                    if not domains[nb]:
                        ok = False
                        break
                if pruned_log:
                    steps.append(Step(
                        kind="prune",
                        pruned=pruned_log,
                        domains_snapshot=deepcopy(domains),
                        assignment_snapshot=dict(assignment),
                        note=f"Forward-check after {var}={value}",
                    ))

            if ok:
                result = backtrack(csp, assignment, domains, steps, use_fc)
                if result is not None:
                    return result

            # Undo
            for v in csp.variables:
                domains[v] = saved[v]
            del assignment[var]
            steps.append(Step(
                kind="unassign", variable=var, value=value,
                domains_snapshot=deepcopy(domains),
                assignment_snapshot=dict(assignment),
                note=f"Backtrack: undo {var}={value}",
            ))

    return None


def solve(csp: CSP, use_ac3=True, use_fc=True) -> tuple:
    domains = {v: set(d) for v, d in csp.domains.items()}
    steps: List[Step] = []
    if use_ac3:
        if not ac3(csp, domains, steps):
            return None, steps
    result = backtrack(csp, {}, domains, steps, use_fc=use_fc)
    return result, steps
