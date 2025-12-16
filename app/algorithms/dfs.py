from __future__ import annotations

from app.algorithms.base import Algorithm, AlgoResult
from app.core.graph import Graph

class DFS(Algorithm):
    def run(self, graph: Graph, **params) -> AlgoResult:
        start = int(params["start"])
        seen: set[int] = set()
        order: list[int] = []

        def go(u: int) -> None:
            seen.add(u)
            order.append(u)
            for v in graph.neighbors(u):
                if v not in seen:
                    go(v)

        go(start)
        return AlgoResult("DFS", {"start": start, "reachable": order})
