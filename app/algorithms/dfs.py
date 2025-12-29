from __future__ import annotations
from typing import Dict, List, Optional
from .base import neighbors


def dfs(graph, start: int) -> Dict:
    stack = [start]
    visited = set()
    parent: Dict[int, Optional[int]] = {start: None}
    order: List[int] = []

    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        order.append(u)

        # DFS hissi için ters sırayla push
        ns = list(neighbors(graph, u))
        ns.reverse()
        for v in ns:
            if v not in visited:
                if v not in parent:
                    parent[v] = u
                stack.append(v)

    return {"order": order, "parent": parent}
