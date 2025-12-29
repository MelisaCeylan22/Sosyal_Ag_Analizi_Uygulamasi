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
        # Node'ları güvenli serialize et
        nodes_out = []
        for nid, n in graph.nodes.items():  # <-- .items() önemli
            nodes_out.append({
                "id": int(getattr(n, "id", nid)),
                "name": str(getattr(n, "name", "")),
                "aktiflik": float(getattr(n, "aktiflik", 0.0)),
                "etkilesim": float(getattr(n, "etkilesim", 0.0)),
                "baglanti_sayisi": int(getattr(n, "baglanti_sayisi", 0)),
                "x": float(getattr(n, "x", 0.0)),
                "y": float(getattr(n, "y", 0.0)),
            })

        # Edge'leri güvenli serialize et
        edges_out = []
        # edges dict olabilir: {(u,v): EdgeObj}
        for (u, v), e in graph.edges.items():
            u2, v2 = undirected_key(int(u), int(v))
            edges_out.append({
                "u": int(u2),
                "v": int(v2),
                "weight": float(getattr(e, "weight", 1.0)),
            })

        data: dict[str, Any] = {
            "type": "social_graph",
            "nodes": nodes_out,
            "edges": edges_out,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_json(path: str) -> Graph:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        g = Graph()

        # nodes
        for row in data.get("nodes", []):
            n = Node(
                id=int(row["id"]),
                name=str(row.get("name", "")),
                aktiflik=float(row.get("aktiflik", 0.0)),
                etkilesim=float(row.get("etkilesim", 0.0)),
                baglanti_sayisi=int(row.get("baglanti_sayisi", 0)),
            )
            # konum varsa yükle
            n.x = float(row.get("x", 0.0))
            n.y = float(row.get("y", 0.0))
            g.add_node(n)

        # edges
        for row in data.get("edges", []):
            u = int(row["u"])
            v = int(row["v"])
            w = float(row.get("weight", 1.0))

            # add_edge weight param kabul etmese bile güvenli set edeceğiz
            e = g.add_edge(u, v, weight_fn=None)
            if hasattr(e, "weight"):
                e.weight = w

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
        return ids, mat
