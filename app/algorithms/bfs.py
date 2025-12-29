from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional
from .base import neighbors


def bfs(graph, start: int) -> Dict:
    q = deque([start])
    visited = set([start])
    parent: Dict[int, Optional[int]] = {start: None}
    order: List[int] = []

    while q:
        u = q.popleft()
        order.append(u)
        for v in neighbors(graph, u):
            if v not in visited:
                visited.add(v)
                parent[v] = u
                q.append(v)

    return {"order": order, "parent": parent}
