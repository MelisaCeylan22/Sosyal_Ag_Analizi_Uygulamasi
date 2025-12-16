from __future__ import annotations
import heapq
from math import inf

from app.algorithms.base import Algorithm, AlgoResult
from app.core.graph import Graph

class Dijkstra(Algorithm):
    def run(self, graph: Graph, **params) -> AlgoResult:
        start = int(params["start"])
        goal = int(params["goal"])

        dist = {nid: inf for nid in graph.nodes.keys()}
        prev: dict[int, int | None] = {nid: None for nid in graph.nodes.keys()}
        dist[start] = 0.0

        pq: list[tuple[float, int]] = [(0.0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d != dist[u]:
                continue
            if u == goal:
                break
            for v in graph.neighbors(u):
                w = graph.get_edge_weight(u, v)
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))

        if dist[goal] == inf:
            path = []
        else:
            path = []
            cur = goal
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            path.reverse()

        return AlgoResult("Dijkstra", {"start": start, "goal": goal, "distance": dist[goal], "path": path})
