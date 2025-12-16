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

    # ---------- Node CRUD ----------
    def add_node(self, node: Node) -> None:
        if node.id in self.nodes:
            raise ValueError(f"Node zaten var: id={node.id}")
        self.nodes[node.id] = node
        self.adj[node.id] = set()

    def update_node(self, node_id: int, **fields) -> None:
        if node_id not in self.nodes:
            raise ValueError(f"Node yok: id={node_id}")
        old = self.nodes[node_id]
        self.nodes[node_id] = replace(old, **fields)

    def remove_node(self, node_id: int) -> None:
        if node_id not in self.nodes:
            return
        # bağlı edge’leri sil
        for nb in list(self.adj.get(node_id, set())):
            self.remove_edge(node_id, nb)
        self.adj.pop(node_id, None)
        self.nodes.pop(node_id, None)

    # ---------- Edge CRUD ----------
    def add_edge(self, u: int, v: int, weight_fn: WeightFn | None = None) -> None:
        if u == v:
            raise ValueError("Self-loop yasak (u == v).")
        if u not in self.nodes or v not in self.nodes:
            raise ValueError("Edge eklemek için iki node da mevcut olmalı.")
        key = undirected_key(u, v)
        if key in self.edges:
            raise ValueError("Bu edge zaten var (yönsüz).")

        w = 1.0
        if weight_fn is not None:
            w = float(weight_fn(self.nodes[u], self.nodes[v]))

        self.edges[key] = Edge(u=key[0], v=key[1], weight=w)
        self.adj[u].add(v)
        self.adj[v].add(u)

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
        for key, e in list(self.edges.items()):
            a = self.nodes[e.u]
            b = self.nodes[e.v]
            e.weight = float(weight_fn(a, b))

    def get_edge_weight(self, u: int, v: int) -> float:
        e = self.edges.get(undirected_key(u, v))
        if not e:
            raise KeyError(f"Edge yok: {u}-{v}")
        return e.weight
