from __future__ import annotations

from app.algorithms.base import Algorithm, AlgoResult
from app.core.graph import Graph

class ConnectedComponents(Algorithm):
    def run(self, graph: Graph, **params) -> AlgoResult:
        seen: set[int] = set()
        comps: list[list[int]] = []

        for nid in graph.nodes:
            if nid in seen:
                continue
            stack = [nid]
            comp: list[int] = []
            seen.add(nid)
            while stack:
                u = stack.pop()
                comp.append(u)
                for v in graph.neighbors(u):
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            comps.append(sorted(comp))

        return AlgoResult("ConnectedComponents", {"components": comps, "count": len(comps)})
