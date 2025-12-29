from __future__ import annotations

import math
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QGroupBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

from app.ui.graph_view import GraphView
from app.ui.graphics_items import NodeItem, EdgeItem

from app.core.storage import StorageService
from app.core.graph import Graph
from app.core.node import Node
from app.core.edge import undirected_key
from app.core.weight_service import WeightService

from app.algorithms.bfs import bfs
from app.algorithms.dfs import dfs
from app.algorithms.dijkstra import dijkstra
from app.algorithms.astar import astar
from app.algorithms.components import connected_components
from app.algorithms.centrality import degree_centrality, closeness_centrality
from app.algorithms.welsh_powell import welsh_powell_coloring

from app.core.mysql_storage import MySqlStorageService

from PySide6.QtWidgets import QScrollArea, QSizePolicy

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView






class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Social Graph - PySide6 (Dynamic Weight + I/O + Labels)")
        self.resize(1100, 700)

        self.graph = Graph()
        self.view = GraphView()
        if hasattr(self.view, "nodeSelected"):
            self.view.nodeSelected.connect(self.on_node_selected)

        self.node_items: dict[int, NodeItem] = {}
        self.edge_items: dict[tuple[int, int], EdgeItem] = {}

        root = QWidget()
        self.setCentralWidget(root)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.view)
        splitter.addWidget(self._build_right_panel())
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        splitter.setSizes([800, 420])


        layout = QVBoxLayout(root)
        layout.addWidget(splitter)

        self._seed_demo()

    def _table_clear(self) -> None:
        if hasattr(self, "tbl") and self.tbl is not None:
            self.tbl.setRowCount(0)

    def _table_add_row(self, typ: str, _id: str, val: str) -> None:
        if not hasattr(self, "tbl") or self.tbl is None:
            return
        r = self.tbl.rowCount()
        self.tbl.insertRow(r)
        self.tbl.setItem(r, 0, QTableWidgetItem(str(typ)))
        self.tbl.setItem(r, 1, QTableWidgetItem(str(_id)))
        self.tbl.setItem(r, 2, QTableWidgetItem(str(val)))


    def _build_right_panel(self) -> QWidget:
        from PySide6.QtWidgets import QScrollArea, QSizePolicy  # local import (istersen en üste de alabilirsin)

        # Scroll: sığmayan kontroller ezilmesin
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(12)

        # ---- Algoritmalar ----
        gA = QGroupBox("Algoritmalar")
        fA = QFormLayout(gA)
        fA.setVerticalSpacing(8)
        fA.setHorizontalSpacing(12)

        self.in_start = QLineEdit("1")
        self.in_goal = QLineEdit("3")
        fA.addRow("Start", self.in_start)
        fA.addRow("Goal", self.in_goal)

        btn_bfs = QPushButton("BFS")
        btn_bfs.clicked.connect(self.bfs_clicked)
        btn_dfs = QPushButton("DFS")
        btn_dfs.clicked.connect(self.dfs_clicked)

        btn_dij = QPushButton("Dijkstra (Start→Goal)")
        btn_dij.clicked.connect(self.dijkstra_clicked)
        btn_ast = QPushButton("A* (Start→Goal)")
        btn_ast.clicked.connect(self.astar_clicked)

        btn_comp = QPushButton("Components")
        btn_comp.clicked.connect(self.components_clicked)

        btn_cent = QPushButton("Centrality (Degree+Closeness)")
        btn_cent.clicked.connect(self.centrality_clicked)

        btn_color = QPushButton("Welsh–Powell (Coloring)")
        btn_color.clicked.connect(self.coloring_clicked)

        for b in (btn_bfs, btn_dfs, btn_dij, btn_ast, btn_comp, btn_cent, btn_color):
            b.setMinimumHeight(30)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        fA.addRow(btn_bfs)
        fA.addRow(btn_dfs)
        fA.addRow(btn_dij)
        fA.addRow(btn_ast)
        fA.addRow(btn_comp)
        fA.addRow(btn_cent)
        fA.addRow(btn_color)

        # ---- Node form ----
        g1 = QGroupBox("Node CRUD")
        f1 = QFormLayout(g1)
        f1.setVerticalSpacing(8)
        f1.setHorizontalSpacing(12)

        self.in_id = QLineEdit()
        self.in_name = QLineEdit()
        self.in_aktiflik = QLineEdit("0.0")
        self.in_etkilesim = QLineEdit("0.0")
        self.in_baglanti = QLineEdit("0")

        f1.addRow("ID", self.in_id)
        f1.addRow("Name", self.in_name)
        f1.addRow("Aktiflik", self.in_aktiflik)
        f1.addRow("Etkileşim", self.in_etkilesim)
        f1.addRow("Bağlantı", self.in_baglanti)

        btn_add = QPushButton("Node Ekle")
        btn_add.clicked.connect(self.add_node_clicked)
        btn_upd = QPushButton("Node Güncelle")
        btn_upd.clicked.connect(self.update_node_clicked)
        btn_del = QPushButton("Node Sil")
        btn_del.clicked.connect(self.delete_node_clicked)

        for b in (btn_add, btn_upd, btn_del):
            b.setMinimumHeight(30)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        f1.addRow(btn_add)
        f1.addRow(btn_upd)
        f1.addRow(btn_del)

        # ---- Edge form ----
        g2 = QGroupBox("Edge CRUD")
        f2 = QFormLayout(g2)
        f2.setVerticalSpacing(8)
        f2.setHorizontalSpacing(12)

        self.in_u = QLineEdit()
        self.in_v = QLineEdit()
        f2.addRow("U", self.in_u)
        f2.addRow("V", self.in_v)

        btn_eadd = QPushButton("Edge Ekle (weight auto)")
        btn_eadd.clicked.connect(self.add_edge_clicked)
        btn_edel = QPushButton("Edge Sil")
        btn_edel.clicked.connect(self.delete_edge_clicked)

        for b in (btn_eadd, btn_edel):
            b.setMinimumHeight(30)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        f2.addRow(btn_eadd)
        f2.addRow(btn_edel)

        # ---- Weight formülü (Dinamik) ----
        gW = QGroupBox("Weight Formülü (katsayılar)")
        fW = QFormLayout(gW)
        fW.setVerticalSpacing(8)
        fW.setHorizontalSpacing(12)

        self.in_a = QLineEdit(str(WeightService.params.a))
        self.in_b = QLineEdit(str(WeightService.params.b))
        self.in_c = QLineEdit(str(WeightService.params.c))

        fW.addRow("a (aktiflik)", self.in_a)
        fW.addRow("b (etkileşim)", self.in_b)
        fW.addRow("c (bağlantı)", self.in_c)

        btn_w_update = QPushButton("Tüm Edge Weight'lerini Güncelle")
        btn_w_update.clicked.connect(self.update_weights_clicked)
        btn_w_show = QPushButton("Edge Weight'lerini Göster")
        btn_w_show.clicked.connect(self.show_weights_clicked)

        for b in (btn_w_update, btn_w_show):
            b.setMinimumHeight(30)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        fW.addRow(btn_w_update)
        fW.addRow(btn_w_show)

        # ---- File I/O + MySQL ----
        g3 = QGroupBox("Dosya (JSON/CSV) + Çıktılar")
        f3 = QFormLayout(g3)
        f3.setVerticalSpacing(8)
        f3.setHorizontalSpacing(12)

        btn_csv_load = QPushButton("CSV Yükle")
        btn_csv_load.clicked.connect(self.csv_load_clicked)
        btn_csv_save = QPushButton("CSV Kaydet")
        btn_csv_save.clicked.connect(self.csv_save_clicked)

        btn_json_load = QPushButton("JSON Yükle")
        btn_json_load.clicked.connect(self.json_load_clicked)
        btn_json_save = QPushButton("JSON Kaydet")
        btn_json_save.clicked.connect(self.json_save_clicked)

        btn_adj_list = QPushButton("Komşuluk Listesi Göster")
        btn_adj_list.clicked.connect(self.show_adj_list_clicked)
        btn_adj_mat = QPushButton("Komşuluk Matrisi Göster")
        btn_adj_mat.clicked.connect(self.show_adj_matrix_clicked)

        btn_db_load = QPushButton("MySQL Yükle")
        btn_db_load.clicked.connect(self.mysql_load_clicked)
        btn_db_save = QPushButton("MySQL Kaydet")
        btn_db_save.clicked.connect(self.mysql_save_clicked)

        for b in (
            btn_csv_load, btn_csv_save, btn_json_load, btn_json_save,
            btn_adj_list, btn_adj_mat, btn_db_load, btn_db_save
        ):
            b.setMinimumHeight(30)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        f3.addRow(btn_csv_load)
        f3.addRow(btn_csv_save)
        f3.addRow(btn_json_load)
        f3.addRow(btn_json_save)
        f3.addRow(btn_adj_list)
        f3.addRow(btn_adj_mat)
        f3.addRow(btn_db_load)
        f3.addRow(btn_db_save)

        # ---- Status ----
        self.lbl = QLabel("Hazır.")
        self.lbl.setWordWrap(True)

        # Sıra: önce algoritmalar sonra diğerleri
        lay.addWidget(gA)
        lay.addWidget(g1)
        lay.addWidget(g2)
        lay.addWidget(gW)
        lay.addWidget(g3)
        lay.addWidget(self.lbl)
        lay.addStretch(1)

        # ---- Sonuç Tablosu ----
        gR = QGroupBox("Sonuçlar")
        rLay = QVBoxLayout(gR)

        self.tbl = QTableWidget(0, 3)
        self.tbl.setHorizontalHeaderLabels(["Tür", "ID", "Değer / Açıklama"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.setMinimumHeight(180)

        rLay.addWidget(self.tbl)

        lay.addWidget(gR)


        scroll.setWidget(content)
        scroll.setMinimumWidth(380)
        return scroll


    # ---------- Demo ----------
    def _seed_demo(self) -> None:
        self._add_node(Node(1, "A", 0.8, 12, 3), x=-120, y=-40)
        self._add_node(Node(2, "B", 0.4, 5, 2), x=60, y=-50)
        self._add_node(Node(3, "C", 0.6, 9, 4), x=0, y=90)
        self._add_edge(1, 2)
        self._add_edge(2, 3)

    # ---------- Selection ----------
    def on_node_selected(self, node_id: int) -> None:
        n = self.graph.nodes.get(node_id)
        if not n:
            return
        self.in_id.setText(str(n.id))
        self.in_name.setText(n.name)
        self.in_aktiflik.setText(str(n.aktiflik))
        self.in_etkilesim.setText(str(n.etkilesim))
        self.in_baglanti.setText(str(n.baglanti_sayisi))

    # ---------- CRUD ----------
    def add_node_clicked(self) -> None:
        try:
            node = self._read_node_inputs()
            self._add_node(node, x=0, y=0)
            self.lbl.setText(f"Node eklendi: {node.id}")
        except Exception as e:
            self.lbl.setText(f"Hata: {e}")

    def update_node_clicked(self) -> None:
        try:
            node = self._read_node_inputs()
            self.graph.update_node(
                node.id,
                name=node.name,
                aktiflik=node.aktiflik,
                etkilesim=node.etkilesim,
                baglanti_sayisi=node.baglanti_sayisi,
            )
            if node.id in self.node_items:
                self.node_items[node.id].set_label(f"{node.id}:{node.name}")

            self.graph.recompute_all_weights(WeightService.compute)
            self._sync_edge_labels()

            self.lbl.setText(f"Node güncellendi: {node.id}")
        except Exception as e:
            self.lbl.setText(f"Hata: {e}")

    def delete_node_clicked(self) -> None:
        try:
            nid = int(self.in_id.text().strip())
            self._remove_node(nid)
            self.lbl.setText(f"Node silindi: {nid}")
        except Exception as e:
            self.lbl.setText(f"Hata: {e}")

    def add_edge_clicked(self) -> None:
        try:
            u = int(self.in_u.text().strip())
            v = int(self.in_v.text().strip())
            e = self._add_edge(u, v)
            self.lbl.setText(f"Edge eklendi: {e.u}-{e.v} w={e.weight:.6f}")
        except Exception as e:
            self.lbl.setText(f"Hata: {e}")

    def delete_edge_clicked(self) -> None:
        try:
            u = int(self.in_u.text().strip())
            v = int(self.in_v.text().strip())
            self._remove_edge(u, v)
            self.lbl.setText(f"Edge silindi: {u}-{v}")
        except Exception as e:
            self.lbl.setText(f"Hata: {e}")

    # ---------- Dynamic weight ----------
    def update_weights_clicked(self) -> None:
        try:
            WeightService.params.a = float(self.in_a.text().strip())
            WeightService.params.b = float(self.in_b.text().strip())
            WeightService.params.c = float(self.in_c.text().strip())

            self.graph.recompute_all_weights(WeightService.compute)
            self._sync_edge_labels()

            self.lbl.setText("Weight güncellendi.")
        except Exception as e:
            self.lbl.setText(f"Hata (weight): {e}")

    def show_weights_clicked(self) -> None:
        if not self.graph.edges:
            QMessageBox.information(self, "Edge Weights", "(Edge yok)")
            return
        lines = [f"{u}-{v}   w={e.weight:.6f}" for (u, v), e in sorted(self.graph.edges.items())]
        QMessageBox.information(self, "Edge Weights", "\n".join(lines))

    def _show_result(self, title: str, out: dict, start=None, goal=None) -> None:
        # tabloyu temizle
        self._table_clear()

        # üst satır: hangi algoritma, start/goal
        meta = []
        if start is not None:
            meta.append(f"Start={start}")
        if goal is not None:
            meta.append(f"Goal={goal}")
        self._table_add_row("ALGO", title, " ".join(meta) if meta else "OK")

        # çıkan order/path/cost gibi alanları satır satır yaz
        if isinstance(out, dict):
            if "order" in out:
                self._table_add_row("ORDER", "-", " -> ".join(map(str, out.get("order", []))))
            if "path" in out:
                self._table_add_row("PATH", "-", " -> ".join(map(str, out.get("path", []))))
            if "cost" in out:
                self._table_add_row("COST", "-", str(out.get("cost"))),
        # --- GRAF ÜSTÜNDE GÖSTERİM ---
        self._clear_highlights()

        if isinstance(out, dict):
            if out.get("path"):
                self._highlight_path(list(out["path"]))
            elif out.get("order"):
                # path yoksa en azından ziyaret sırasındaki node'ları parlat
                self._highlight_nodes(list(out["order"]))

    
    
    def _clear_highlights(self) -> None:
        for it in self.node_items.values():
            if hasattr(it, "set_highlight"):
                it.set_highlight(False)
        for it in self.edge_items.values():
            if hasattr(it, "set_highlight"):
                it.set_highlight(False)

    def _highlight_nodes(self, node_ids: list[int]) -> None:
        for nid in node_ids:
            it = self.node_items.get(nid)
            if it and hasattr(it, "set_highlight"):
                it.set_highlight(True)

    def _highlight_path(self, path: list[int]) -> None:
        if not path:
            return
        self._highlight_nodes(path)

        # path üzerindeki edge'leri de parlat
        for u, v in zip(path, path[1:]):
            key = undirected_key(u, v)  # yönsüz key
            eit = self.edge_items.get(key)
            if eit and hasattr(eit, "set_highlight"):
                eit.set_highlight(True)



    
    # ---------- File handlers ----------
    def csv_load_clicked(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "CSV Seç", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            self.graph = StorageService.load_csv(path)
            self.graph.recompute_all_weights(WeightService.compute)
            self._render_graph()
            self._sync_edge_labels()
            self.lbl.setText(f"CSV yüklendi: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def csv_save_clicked(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "CSV Kaydet", "graph.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            StorageService.save_csv(self.graph, path)
            self.lbl.setText(f"CSV kaydedildi: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def json_load_clicked(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "JSON Seç", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            self.graph = StorageService.load_json(path)
            self.graph.recompute_all_weights(WeightService.compute)
            self._render_graph()
            self._sync_edge_labels()
            self.lbl.setText(f"JSON yüklendi: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def json_save_clicked(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "JSON Kaydet", "graph.json", "JSON Files (*.json)")
        if not path:
            return
        try:
            StorageService.save_json(self.graph, path)
            self.lbl.setText(f"JSON kaydedildi: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def show_adj_list_clicked(self) -> None:
        adj = StorageService.adjacency_list(self.graph)
        text = "\n".join([f"{k}: {v}" for k, v in adj.items()])
        QMessageBox.information(self, "Komşuluk Listesi", text if text else "(Boş)")

    def show_adj_matrix_clicked(self) -> None:
        res = StorageService.adjacency_matrix(self.graph)

        # res bazen (ids, mat) bazen (ids, mat, something) döndürebilir
        if isinstance(res, tuple) and len(res) >= 2:
            ids, mat = res[0], res[1]
        else:
            QMessageBox.critical(self, "Hata", "adjacency_matrix beklenmeyen çıktı döndürdü.")
            return

        if not ids:
            QMessageBox.information(self, "Komşuluk Matrisi", "(Boş)")
            return

        header = "    " + " ".join([str(i).rjust(3) for i in ids])
        lines = [header]
        for rid, row in zip(ids, mat):
            lines.append(str(rid).rjust(3) + " " + " ".join([str(x).rjust(3) for x in row]))

        QMessageBox.information(self, "Komşuluk Matrisi", "\n".join(lines))


    # ---------- Render ----------
    def _clear_scene(self) -> None:
        self.view.scene.clear()
        self.node_items = {}
        self.edge_items = {}

    def _render_graph(self) -> None:
        self._clear_scene()
        ids = sorted(self.graph.nodes.keys())
        n = len(ids)
        if n == 0:
            return

        R = 220.0
        for i, nid in enumerate(ids):
            angle = 2 * math.pi * i / n
            x = R * math.cos(angle)
            y = R * math.sin(angle)

            node = self.graph.nodes[nid]
            item = NodeItem(nid, label=f"{nid}:{node.name}")
            item.setPos(x, y)
            self.view.scene.addItem(item)
            self.node_items[nid] = item

        for (u, v), _e in self.graph.edges.items():
            key = undirected_key(u, v)
            a = self.node_items[key[0]]
            b = self.node_items[key[1]]
            eit = EdgeItem(a, b, weight=_e.weight)
            self.view.scene.addItem(eit)
            self.edge_items[key] = eit

    def _sync_edge_labels(self) -> None:
        for (u, v), e in self.graph.edges.items():
            key = undirected_key(u, v)
            it = self.edge_items.get(key)
            if it and hasattr(it, "set_weight"):
                it.set_weight(e.weight)

    # ---------- Helpers ----------
    def _read_node_inputs(self) -> Node:
        return Node(
            id=int(self.in_id.text().strip()),
            name=self.in_name.text().strip(),
            aktiflik=float(self.in_aktiflik.text().strip()),
            etkilesim=float(self.in_etkilesim.text().strip()),
            baglanti_sayisi=int(self.in_baglanti.text().strip()),
        )

    def _add_node(self, node: Node, x: float, y: float) -> None:
        self.graph.add_node(node)
        item = NodeItem(node.id, label=f"{node.id}:{node.name}")
        item.setPos(x, y)
        self.view.scene.addItem(item)
        self.node_items[node.id] = item

    def _remove_node(self, node_id: int) -> None:
        for nb in list(self.graph.neighbors(node_id)):
            self._remove_edge(node_id, nb)
        self.graph.remove_node(node_id)
        it = self.node_items.pop(node_id, None)
        if it:
            self.view.scene.removeItem(it)

    def _add_edge(self, u: int, v: int):
        e = self.graph.add_edge(u, v, weight_fn=WeightService.compute)
        key = undirected_key(u, v)

        a = self.node_items[key[0]]
        b = self.node_items[key[1]]

        eit = EdgeItem(a, b, weight=e.weight)
        self.view.scene.addItem(eit)
        self.edge_items[key] = eit
        return e

    def _remove_edge(self, u: int, v: int) -> None:
        key = undirected_key(u, v)
        self.graph.remove_edge(u, v)
        eit = self.edge_items.pop(key, None)
        if eit:
            self.view.scene.removeItem(eit)

    def _read_start_goal(self):
        s = int(self.in_start.text().strip())
        g = int(self.in_goal.text().strip())
        return s, g
    

    def bfs_clicked(self):
        try:
            s, _ = self._read_start_goal()
            out = bfs(self.graph, s)

            self._show_result("BFS", out, start=s)  # <<< 1 satır

            QMessageBox.information(self, "BFS", f"Order:\n{out['order']}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))



    def dfs_clicked(self):
        try:
            s, _ = self._read_start_goal()
            out = dfs(self.graph, s)

            self._show_result("DFS", out, start=s)

            QMessageBox.information(self, "DFS", f"Order:\n{out['order']}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def dijkstra_clicked(self):
        try:
            s, g = self._read_start_goal()
            out = dijkstra(self.graph, s, g)

            self._show_result("Dijkstra", out, start=s, goal=g)

            QMessageBox.information(self, "Dijkstra", f"Path: {out['path']}\nCost: {out['cost']}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def astar_clicked(self):
        try:
            s, g = self._read_start_goal()
            out = astar(self.graph, s, g)

            self._show_result("A*", out, start=s, goal=g)
            
            QMessageBox.information(self, "A*", f"Path: {out['path']}\nCost: {out['cost']}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def components_clicked(self):
        try:
            comps = connected_components(self.graph)
            text = "\n".join([f"{i+1}) {c}" for i, c in enumerate(comps)])
            QMessageBox.information(self, "Components", text if text else "(Boş)")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def centrality_clicked(self):
        try:
            deg = degree_centrality(self.graph)
            clo = closeness_centrality(self.graph)

            top_deg = sorted(deg.items(), key=lambda x: x[1], reverse=True)[:5]
            top_clo = sorted(clo.items(), key=lambda x: x[1], reverse=True)[:5]

            msg = "Top Degree:\n" + "\n".join([f"{nid}: {v:.4f}" for nid, v in top_deg])
            msg += "\n\nTop Closeness:\n" + "\n".join([f"{nid}: {v:.4f}" for nid, v in top_clo])

            QMessageBox.information(self, "Centrality", msg)
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def coloring_clicked(self):
        try:
            coloring = welsh_powell_coloring(self.graph)
            k = (max(coloring.values()) + 1) if coloring else 0

            # UI label’a renk numarası ekleyelim (görsel kanıt)
            for nid, col in coloring.items():
                n = self.graph.nodes.get(nid)
                name = n.name if n else ""
                if nid in self.node_items:
                    self.node_items[nid].set_label(f"{nid}:{name} (c{col})")

            text = f"Renk sayısı: {k}\n\n" + "\n".join([f"{nid} -> c{col}" for nid, col in sorted(coloring.items())])
            QMessageBox.information(self, "Welsh–Powell", text)
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def mysql_save_clicked(self) -> None:
        try:
            MySqlStorageService.save_graph(self.graph, graph_id=1, name="SocialGraph")
            self.lbl.setText("MySQL kaydedildi (graph_id=1).")
        except Exception as e:
            QMessageBox.critical(self, "MySQL Hata", str(e))

    def mysql_load_clicked(self) -> None:
        try:
            self.graph = MySqlStorageService.load_graph(graph_id=1)
            # dinamik weight istiyorsan yeniden hesapla:
            self.graph.recompute_all_weights(WeightService.compute)
            self._render_graph()
            if hasattr(self, "_sync_edge_labels"):
                self._sync_edge_labels()
            self.lbl.setText("MySQL yüklendi (graph_id=1).")
        except Exception as e:
            QMessageBox.critical(self, "MySQL Hata", str(e))





    



