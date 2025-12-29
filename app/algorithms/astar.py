from __future__ import annotations
import heapq
import math
from typing import Dict, Optional, Tuple, List
from .base import neighbors, edge_weight, reconstruct_path, node_pos


def heuristic(graph, a: int, b: int) -> float:
    ax, ay = node_pos(graph, a)
    bx, by = node_pos(graph, b)
    return math.hypot(ax - bx, ay - by)


def astar(graph, start: int, goal: int) -> Dict:
    g: Dict[int, float] = {start: 0.0}
    prev: Dict[int, Optional[int]] = {start: None}
    pq: List[Tuple[float, int]] = [(heuristic(graph, start, goal), start)]
    closed = set()

    while pq:
        f, u = heapq.heappop(pq)
        if u in closed:
            continue
        if u == goal:
            break
        closed.add(u)

        for v in neighbors(graph, u):
            w = edge_weight(graph, u, v)
            ng = g[u] + w
            if v not in g or ng < g[v]:
                g[v] = ng
                prev[v] = u
                nf = ng + heuristic(graph, v, goal)
                heapq.heappush(pq, (nf, v))

    path = reconstruct_path(prev, start, goal)
    return {"g": g, "prev": prev, "path": path, "cost": g.get(goal, float("inf"))}
