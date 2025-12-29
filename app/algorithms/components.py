from __future__ import annotations
from typing import List, Set
from collections import deque
from .base import neighbors


def connected_components(graph) -> List[List[int]]:
    nodes = sorted(getattr(graph, "nodes", {}).keys())
    visited: Set[int] = set()
    comps: List[List[int]] = []

    for s in nodes:
        if s in visited:
            continue
        q = deque([s])
        visited.add(s)
        comp = []
        while q:
            u = q.popleft()
            comp.append(u)
            for v in neighbors(graph, u):
                if v not in visited:
                    visited.add(v)
                    q.append(v)
        comps.append(comp)

    return comps
