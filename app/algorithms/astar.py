from __future__ import annotations
import heapq
from math import inf, sqrt

from app.algorithms.base import Algorithm, AlgoResult
from app.core.graph import Graph

class AStar(Algorithm):
    def run(self, graph: Graph, **params) -> AlgoResult:
        start = int(params["start"])
        goal = int(params["goal"])

        def h(a: int, b: int) -> float:
            na = graph.nodes[a]
            nb = graph.nodes[b]
            # UI konumu varsa öklid; yoksa 0
            return sqrt((na.x - nb.x) ** 2 + (na.y - nb.y) ** 2)

        gscore = {nid: inf for nid in graph.nodes}
        fscore = {nid: inf for nid in graph.nodes}
        came: dict[int, int | None] = {nid: None for nid in graph.nodes}

        gscore[start] = 0.0
        fscore[start] = h(start, goal)

        pq: list[tuple[float, int]] = [(fscore[start], start)]
        while pq:
            _, u = heapq.heappop(pq)
            if u == goal:
                break
            for v in graph.neighbors(u):
                tentative = gscore[u] + graph.get_edge_weight(u, v)
                if tentative < gscore[v]:
                    came[v] = u
                    gscore[v] = tentative
                    fscore[v] = tentative + h(v, goal)
                    heapq.heappush(pq, (fscore[v], v))

        if gscore[goal] == inf:
            path = []
        else:
            path = []
            cur = goal
            while cur is not None:
                path.append(cur)
                cur = came[cur]
            path.reverse()

        return AlgoResult("A*", {"start": start, "goal": goal, "distance": gscore[goal], "path": path})
