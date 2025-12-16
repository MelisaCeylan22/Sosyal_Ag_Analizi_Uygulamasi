from __future__ import annotations

from app.algorithms.base import Algorithm, AlgoResult
from app.core.graph import Graph

class DegreeCentrality(Algorithm):
    def run(self, graph: Graph, **params) -> AlgoResult:
        rows = []
        for nid in graph.nodes:
            rows.append((nid, graph.degree(nid)))
        rows.sort(key=lambda x: x[1], reverse=True)
        top5 = rows[:5]
        return AlgoResult("DegreeCentrality", {"degrees": rows, "top5": top5})
