from __future__ import annotations
from typing import Dict
from .base import neighbors
from .dijkstra import dijkstra


def degree_centrality(graph) -> Dict[int, float]:
    nodes = list(getattr(graph, "nodes", {}).keys())
    n = len(nodes)
    if n <= 1:
        return {nid: 0.0 for nid in nodes}

    deg = {nid: len(list(neighbors(graph, nid))) for nid in nodes}
    return {nid: deg[nid] / (n - 1) for nid in nodes}


def closeness_centrality(graph) -> Dict[int, float]:
    nodes = list(getattr(graph, "nodes", {}).keys())
    n = len(nodes)
    if n <= 1:
        return {nid: 0.0 for nid in nodes}

    res: Dict[int, float] = {}
    for s in nodes:
        out = dijkstra(graph, s)  # dist tüm düğümlere
        dist = out["dist"]
        # ulaşamadıklarını sayma (inf gibi davran)
        reachable = [d for (nid, d) in dist.items() if nid != s]
        if not reachable:
            res[s] = 0.0
            continue
        total = sum(reachable)
        res[s] = (len(reachable) / total) if total > 0 else 0.0
    return res
