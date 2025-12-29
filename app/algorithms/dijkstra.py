from __future__ import annotations
import heapq
from typing import Dict, Optional, Tuple, List
from .base import neighbors, edge_weight, reconstruct_path


def dijkstra(graph, start: int, goal: Optional[int] = None) -> Dict:
    dist: Dict[int, float] = {start: 0.0}
    prev: Dict[int, Optional[int]] = {start: None}
    pq: List[Tuple[float, int]] = [(0.0, start)]
    seen = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in seen:
            continue
        seen.add(u)

        if goal is not None and u == goal:
            break

        for v in neighbors(graph, u):
            w = edge_weight(graph, u, v)
            nd = d + w
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    path = []
    if goal is not None:
        path = reconstruct_path(prev, start, goal)

    return {"dist": dist, "prev": prev, "path": path, "cost": dist.get(goal, float("inf")) if goal is not None else None}
