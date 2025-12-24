from __future__ import annotations
import csv
import json
from pathlib import Path

from app.core.graph import Graph
from app.core.node import Node
from app.core.edge import undirected_key, Edge
from app.core.weight_service import WeightService


class StorageService:
    # ---------------- JSON ----------------
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

    # ---------------- CSV ----------------
    # Beklenen kolonlar (hocanın örneğine yakın):
    # DugumId, Aktiflik, Etkilesim, Baglanti Sayisi, Komsular
    # Komsular örn: "2 3 4" veya "2,3,4"
    @staticmethod
    def load_csv(path: str) -> Graph:
        g = Graph()
        rows: list[dict[str, str]] = []

        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)

        def get_col(r: dict[str, str], *names: str) -> str:
            for name in names:
                if name in r and r[name] is not None:
                    return str(r[name]).strip()
            return ""

        # 1) Node'ları ekle
        for r in rows:
            nid = int(get_col(r, "DugumId", "dugumId", "id"))
            aktiflik = float(get_col(r, "Aktiflik", "aktiflik", "Activity").replace(",", ".") or "0")
            etkilesim = float(get_col(r, "Etkilesim", "etkilesim", "Interaction").replace(",", ".") or "0")
            # Bağlantı sayısını CSV’de veriyor olabilir ama biz komşulardan tekrar hesaplayacağız
            _baglanti = get_col(r, "Baglanti Sayisi", "BaglantiSayisi", "baglanti", "Degree")
            baglanti = int(_baglanti) if _baglanti else 0

            g.add_node(Node(
                id=nid,
                name=str(nid),
                aktiflik=aktiflik,
                etkilesim=etkilesim,
                baglanti_sayisi=baglanti,
            ))

        # 2) Komşulardan edge kur
        for r in rows:
            u = int(get_col(r, "DugumId", "dugumId", "id"))
            komsular = get_col(r, "Komsular", "Komşular", "neighbors", "Neighbors")
            if not komsular:
                continue

            parts = komsular.replace(",", " ").split()
            for p in parts:
                try:
                    v = int(p)
                except ValueError:
                    continue
                if v not in g.nodes:
                    continue
                try:
                    g.add_edge(u, v, weight_fn=WeightService.compute)
                except ValueError:
                    # duplicate / self-loop vs.
                    pass

        # 3) Bağlantı sayısını gerçek degree’den güncelle (komşulardan türetelim)
        for nid in g.nodes:
            g.nodes[nid].baglanti_sayisi = g.degree(nid)

        # 4) Weight'leri garanti olsun diye tekrar hesapla
        g.recompute_all_weights(WeightService.compute)

        return g

    @staticmethod
    def save_csv(graph: Graph, path: str) -> None:
        # CSV’ye her node’u satır yapalım
        # Komsular: "2 3 4" biçiminde
        fieldnames = ["DugumId", "Aktiflik", "Etkilesim", "Baglanti Sayisi", "Komsular"]
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for nid in sorted(graph.nodes):
                n = graph.nodes[nid]
                komsular = " ".join(map(str, graph.neighbors(nid)))
                w.writerow({
                    "DugumId": n.id,
                    "Aktiflik": n.aktiflik,
                    "Etkilesim": n.etkilesim,
                    "Baglanti Sayisi": graph.degree(nid),
                    "Komsular": komsular
                })

    # ---------------- Adjacency outputs ----------------
    @staticmethod
    def adjacency_list(graph: Graph) -> dict[int, list[int]]:
        return {nid: graph.neighbors(nid) for nid in sorted(graph.nodes)}

    @staticmethod
    def adjacency_matrix(graph: Graph) -> tuple[list[int], list[list[int]]]:
        ids = sorted(graph.nodes)
        idx = {nid: i for i, nid in enumerate(ids)}
        n = len(ids)
        mat = [[0] * n for _ in range(n)]
        for (u, v) in graph.edges.keys():
            i, j = idx[u], idx[v]
            mat[i][j] = 1
            mat[j][i] = 1
        return ids
