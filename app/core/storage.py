from __future__ import annotations
import json
from pathlib import Path

from app.core.graph import Graph
from app.core.node import Node
from app.core.edge import undirected_key, Edge

class StorageService:
    @staticmethod
    def save_json(graph: Graph, path: str) -> None:
        data = {
            "nodes": [vars(n) for n in graph.nodes.values()],
            "edges": [{"u": e.u, "v": e.v, "weight": e.weight} for e in graph.edges.values()],
        }
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def load_json(path: str) -> Graph:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        g = Graph()
        for n in raw.get("nodes", []):
            g.add_node(Node(**n))
        for e in raw.get("edges", []):
            u, v = int(e["u"]), int(e["v"])
            key = undirected_key(u, v)
            g.edges[key] = Edge(u=key[0], v=key[1], weight=float(e.get("weight", 1.0)))
            g.adj[u].add(v)
            g.adj[v].add(u)
        return g
