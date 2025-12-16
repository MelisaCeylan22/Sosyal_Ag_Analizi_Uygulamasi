from __future__ import annotations
from dataclasses import dataclass

def undirected_key(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)

@dataclass(slots=True)
class Edge:
    u: int
    v: int
    weight: float = 1.0

