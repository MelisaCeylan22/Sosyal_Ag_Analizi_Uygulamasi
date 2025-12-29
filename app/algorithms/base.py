from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Iterable, Tuple
from app.core.edge import undirected_key


def neighbors(graph, u: int) -> Iterable[int]:
    # Graph sınıfında neighbors(u) varsa onu kullan
    if hasattr(graph, "neighbors"):
        return list(graph.neighbors(u))
    # yoksa (fallback) edges üzerinden üret
    res = []
    for (a, b) in getattr(graph, "edges", {}).keys():
        if a == u:
            res.append(b)
        elif b == u:
            res.append(a)
    return res


def edge_weight(graph, u: int, v: int) -> float:
    key = undirected_key(u, v)
    e = getattr(graph, "edges", {}).get(key)
    if e is None:
        # bazı implementasyonlar (u,v) tutabilir
        e = getattr(graph, "edges", {}).get((u, v)) or getattr(graph, "edges", {}).get((v, u))
    if e is None:
        return 1.0
    return float(getattr(e, "weight", 1.0))


def reconstruct_path(prev: Dict[int, Optional[int]], start: int, goal: int) -> List[int]:
    if goal not in prev:
        return []
    cur = goal
    path = [cur]
    while cur != start:
        cur = prev.get(cur)
        if cur is None:
            return []
        path.append(cur)
    path.reverse()
    return path


def node_pos(graph, nid: int) -> Tuple[float, float]:
    n = getattr(graph, "nodes", {}).get(nid)
    if not n:
        return (0.0, 0.0)
    x = float(getattr(n, "x", 0.0))
    y = float(getattr(n, "y", 0.0))
    return (x, y)
