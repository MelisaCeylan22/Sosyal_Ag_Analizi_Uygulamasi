from __future__ import annotations

from app.algorithms.base import Algorithm, AlgoResult
from app.core.graph import Graph

class WelshPowellColoring(Algorithm):
    def run(self, graph: Graph, **params) -> AlgoResult:
        # Greedy: düğümleri dereceye göre sırala
        order = sorted(list(graph.nodes.keys()), key=lambda n: graph.degree(n), reverse=True)
        color: dict[int, int] = {}

        for u in order:
            used = {color[v] for v in graph.neighbors(u) if v in color}
            c = 0
            while c in used:
                c += 1
            color[u] = c

        return AlgoResult("WelshPowell", {"coloring": color, "num_colors": (max(color.values()) + 1 if color else 0)})
