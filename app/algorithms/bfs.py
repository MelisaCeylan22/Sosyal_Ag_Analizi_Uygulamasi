from __future__ import annotations
from collections import deque

from app.algorithms.base import Algorithm, AlgoResult
from app.core.graph import Graph

class BFS(Algorithm):
    def run(self, graph: Graph, **params) -> AlgoResult:
        start = int(params["start"])
        seen = set([start])
        q = deque([start])
        order: list[int] = []

        while q:
            u = q.popleft()
            order.append(u)
            for v in graph.neighbors(u):
                if v not in seen:
                    seen.add(v)
                    q.append(v)

        return AlgoResult("BFS", {"start": start, "reachable": order})
