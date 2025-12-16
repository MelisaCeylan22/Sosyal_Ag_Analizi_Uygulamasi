from __future__ import annotations
from dataclasses import replace
from typing import Callable

from app.core.node import Node
from app.core.edge import Edge, undirected_key

WeightFn = Callable[[Node, Node], float]

class Graph:
    def __init__(self) -> None:
        self.nodes: dict[int, Node] = {}
        self.edges: dict[tuple[int, int], Edge] = {}
        self.adj: dict[int, set[int]] = {}

    # ---- Node CRUD ----
    def add_node(self, node: Node) -> None:
        if node.id in self.nodes:
            raise ValueError(f"Duplicate node id: {node.id}")
        self.nodes[node.id] = node
        self.adj[node.id] = set()

    def update_node(self, node_id: int, **fields) -> None:
        if node_id not in self.nodes:
            raise ValueError(f"Node yok: id={node_id}")
        self.nodes[node_id] = replace(self.nodes[node_id], **fields)

    def remove_node(self, node_id: int) -> None:
        if node_id not in self.nodes:
            return
        # bağlı edge’leri temizle
        for nb in list(self.adj[node_id]):
            self.remove_edge(node_id, nb)
        self.adj.pop(node_id, None)
        self.nodes.pop(node_id, None)

    # ---- Edge CRUD ----
    def add_edge(self, u: int, v: int, weight_fn: WeightFn | None = None) -> Edge:
        if u == v:
            raise ValueError("Self-loop yasak (u == v).")
        if u not in self.nodes or v not in self.nodes:
            raise ValueError("Edge eklemek için iki node da mevcut olmalı.")
        key = undirected_key(u, v)
        if key in self.edges:
            raise ValueError("Duplicate edge (yönsüz).")

        w = 1.0
        if weight_fn:
            w = float(weight_fn(self.nodes[u], self.nodes[v]))

        e = Edge(u=key[0], v=key[1], weight=w)
        self.edges[key] = e
        self.adj[u].add(v)
        self.adj[v].add(u)
        return e

    def remove_edge(self, u: int, v: int) -> None:
        key = undirected_key(u, v)
        self.edges.pop(key, None)
        if u in self.adj:
            self.adj[u].discard(v)
        if v in self.adj:
            self.adj[v].discard(u)

    def neighbors(self, node_id: int) -> list[int]:
        return sorted(self.adj.get(node_id, set()))

    def degree(self, node_id: int) -> int:
        return len(self.adj.get(node_id, set()))

    def recompute_all_weights(self, weight_fn: WeightFn) -> None:
        for e in self.edges.values():
            a = self.nodes[e.u]
            b = self.nodes[e.v]
            e.weight = float(weight_fn(a, b))
