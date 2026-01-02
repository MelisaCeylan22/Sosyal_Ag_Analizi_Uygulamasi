from __future__ import annotations

import math
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QGroupBox, QFileDialog, QMessageBox,
    QDialog, QTextEdit
)
from PySide6.QtCore import Qt

from app.ui.graph_view import GraphView
from app.ui.graphics_items import NodeItem, EdgeItem
from app.ui.test_dialog import TestDialog

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

from PySide6.QtWidgets import QScrollArea, QSizePolicy

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

import random
import time



import random
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox









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
        # --- animasyon state ---
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._anim_step)
        self._anim_order: list[int] = []
        self._anim_parent: dict[int, int | None] = {}
        self._anim_idx = 0
        self._anim_prev: int | None = None
        self._anim_last_edge_key: tuple[int, int] | None = None


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

        btn_test = QPushButton("Tüm Algoritmaları Test Et")
        btn_test.clicked.connect(self.test_all_algorithms)

        for b in (btn_bfs, btn_dfs, btn_dij, btn_ast, btn_comp, btn_cent, btn_color, btn_test):
            b.setMinimumHeight(30)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        fA.addRow(btn_bfs)
        fA.addRow(btn_dfs)
        fA.addRow(btn_dij)
        fA.addRow(btn_ast)
        fA.addRow(btn_comp)
        fA.addRow(btn_cent)
        fA.addRow(btn_color)
        fA.addRow(btn_test)

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

        # ---- File I/O ----
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

        for b in (
            btn_csv_load, btn_csv_save, btn_json_load, btn_json_save,
            btn_adj_list, btn_adj_mat
        ):
            b.setMinimumHeight(30)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        f3.addRow(btn_csv_load)
        f3.addRow(btn_csv_save)
        f3.addRow(btn_json_load)
        f3.addRow(btn_json_save)
        f3.addRow(btn_adj_list)
        f3.addRow(btn_adj_mat)

        # ---- Status ----
        self.lbl = QLabel("Hazır.")
        self.lbl.setWordWrap(True)

                # ---- Test grafı üret (Rastgele) ----
        gT = QGroupBox("Test Grafı (Rastgele)")
        fT = QFormLayout(gT)

        self.sp_test_n = QSpinBox()
        self.sp_test_n.setRange(2, 5000)
        self.sp_test_n.setValue(15)

        self.sp_test_p = QDoubleSpinBox()
        self.sp_test_p.setRange(0.01, 1.0)
        self.sp_test_p.setSingleStep(0.01)
        self.sp_test_p.setValue(0.20)

        btn_make = QPushButton("Rastgele Graf Oluştur")
        btn_make.clicked.connect(self.make_random_graph_clicked)

        fT.addRow("Düğüm sayısı (n)", self.sp_test_n)
        fT.addRow("Yoğunluk (p)", self.sp_test_p)
        fT.addRow(btn_make)

        # ---- Animasyon ----
        gAnim = QGroupBox("Animasyon")
        fAnim = QFormLayout(gAnim)

        self.sp_anim_ms = QSpinBox()
        self.sp_anim_ms.setRange(10, 5000)
        self.sp_anim_ms.setValue(250)

        btn_stop_anim = QPushButton("Animasyonu Durdur")
        btn_stop_anim.clicked.connect(self.stop_animation)

        fAnim.addRow("Adım süresi (ms)", self.sp_anim_ms)
        fAnim.addRow(btn_stop_anim)

        lay.addWidget(gT)
        lay.addWidget(gAnim)


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
        self._show_text_dialog("Edge Weights", "\n".join(lines))

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
        if not text:
            QMessageBox.information(self, "Komşuluk Listesi", "(Boş)")
        else:
            self._show_text_dialog("Komşuluk Listesi", text)

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

        self._show_text_dialog("Komşuluk Matrisi", "\n".join(lines))


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

    def _show_text_dialog(self, title: str, text: str, w: int = 700, h: int = 600) -> None:
        """Show a scrollable dialog with long text (read-only)."""
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(w, h)

        lay = QVBoxLayout(dlg)
        te = QTextEdit()
        te.setReadOnly(True)
        te.setPlainText(text)
        te.setStyleSheet("font-family: Courier New; font-size: 10pt;")
        lay.addWidget(te)

        btn = QPushButton("Kapat")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)

        dlg.exec()

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
            self._show_result("BFS", out)  # sende varsa
            order = out.get("order", [])
            parent = out.get("parent", {})
            self.animate_traversal(order, parent, title="BFS")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))




    def dfs_clicked(self):
        try:
            s, _ = self._read_start_goal()
            out = dfs(self.graph, s)
            self._show_result("DFS", out)
            order = out.get("order", [])
            parent = out.get("parent", {})
            self.animate_traversal(order, parent, title="DFS")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))


    def dijkstra_clicked(self):
        try:
            s, g = self._read_start_goal()
            out = dijkstra(self.graph, s, g)

            self._show_result("Dijkstra", out, start=s, goal=g)

            # Animasyon için order'ı oluştur (prev'den)
            prev = out.get("prev", {})
            order = []
            # Ziyaret edilen düğümleri sıra ile ekle
            visited = set()
            for nid in sorted(prev.keys()):
                if nid not in visited:
                    order.append(nid)
                    visited.add(nid)
            
            self.animate_traversal(order, prev, title="Dijkstra")

            QMessageBox.information(self, "Dijkstra", f"Path: {out['path']}\nCost: {out['cost']}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def astar_clicked(self):
        try:
            s, g = self._read_start_goal()
            out = astar(self.graph, s, g)

            self._show_result("A*", out, start=s, goal=g)
            
            # Animasyon için order'ı oluştur (prev'den)
            prev = out.get("prev", {})
            order = []
            # Ziyaret edilen düğümleri sıra ile ekle
            visited = set()
            for nid in sorted(prev.keys()):
                if nid not in visited:
                    order.append(nid)
                    visited.add(nid)
            
            self.animate_traversal(order, prev, title="A*")
            
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

            # UI label'a renk numarası ekleyelim ve düğüme renk ata
            for nid, col in coloring.items():
                n = self.graph.nodes.get(nid)
                name = n.name if n else ""
                if nid in self.node_items:
                    self.node_items[nid].set_label(f"{nid}:{name} (c{col})")
                    self.node_items[nid].set_color(col)

            text = f"Renk sayısı: {k}\n\n" + "\n".join([f"{nid} -> c{col}" for nid, col in sorted(coloring.items())])
            self._show_text_dialog("Welsh–Powell", text)
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def test_all_algorithms(self) -> None:
        """
        Tüm algoritmaları test eder ve sonuçlarını popup dialog'da adım adım gösterir.
        """
        try:
            if not self.graph.nodes:
                QMessageBox.warning(self, "Uyarı", "Lütfen önce bir graf oluşturun.")
                return

            # Dialog oluştur
            dlg = TestDialog(self)
            dlg.clear_results()

            # Grafik bilgisi
            n_nodes = len(self.graph.nodes)
            n_edges = len(self.graph.edges)
            
            dlg.add_result(f"📊 GRAF BİLGİSİ")
            dlg.add_result(f"  Düğüm Sayısı: {n_nodes}")
            dlg.add_result(f"  Edge Sayısı: {n_edges}")
            dlg.add_result(f"  Yoğunluk: {2*n_edges/(n_nodes*(n_nodes-1)) if n_nodes > 1 else 0:.4f}")
            dlg.add_separator()

            # BFS Testi
            dlg.add_result(f"\n1️⃣  BFS Algoritması Çalışıyor...")
            try:
                s, _ = self._read_start_goal()
                t0 = time.perf_counter()
                out = bfs(self.graph, s)
                t1 = time.perf_counter()
                bfs_time = (t1 - t0) * 1000
                
                order = out.get("order", [])
                dlg.add_result(f"✅ BFS Tamamlandı")
                dlg.add_result(f"  Ziyaret Sayısı: {len(order)}")
                dlg.add_result(f"  Ziyaret Sırası: {' → '.join(map(str, order[:15]))}{'...' if len(order) > 15 else ''}")
                dlg.add_result(f"  Çalışma Süresi: {bfs_time:.4f} ms")
            except Exception as e:
                dlg.add_result(f"❌ BFS Hatası: {str(e)}")

            dlg.add_separator()

            # DFS Testi
            dlg.add_result(f"\n2️⃣  DFS Algoritması Çalışıyor...")
            try:
                s, _ = self._read_start_goal()
                t0 = time.perf_counter()
                out = dfs(self.graph, s)
                t1 = time.perf_counter()
                dfs_time = (t1 - t0) * 1000
                
                order = out.get("order", [])
                dlg.add_result(f"✅ DFS Tamamlandı")
                dlg.add_result(f"  Ziyaret Sayısı: {len(order)}")
                dlg.add_result(f"  Ziyaret Sırası: {' → '.join(map(str, order[:15]))}{'...' if len(order) > 15 else ''}")
                dlg.add_result(f"  Çalışma Süresi: {dfs_time:.4f} ms")
            except Exception as e:
                dlg.add_result(f"❌ DFS Hatası: {str(e)}")

            dlg.add_separator()

            # Dijkstra Testi
            dlg.add_result(f"\n3️⃣  Dijkstra Algoritması Çalışıyor...")
            try:
                s, g = self._read_start_goal()
                t0 = time.perf_counter()
                out = dijkstra(self.graph, s, g)
                t1 = time.perf_counter()
                dij_time = (t1 - t0) * 1000
                
                path = out.get("path", [])
                cost = out.get("cost")
                dlg.add_result(f"✅ Dijkstra Tamamlandı")
                dlg.add_result(f"  Başlangıç: {s}, Hedef: {g}")
                dlg.add_result(f"  Yol Uzunluğu: {len(path)}")
                dlg.add_result(f"  Yol: {' → '.join(map(str, path))}")
                dlg.add_result(f"  Toplam Maliyet: {cost:.6f}" if cost else "  Yol Bulunamamıştır!")
                dlg.add_result(f"  Çalışma Süresi: {dij_time:.4f} ms")
            except Exception as e:
                dlg.add_result(f"❌ Dijkstra Hatası: {str(e)}")

            dlg.add_separator()

            # A* Testi
            dlg.add_result(f"\n4️⃣  A* Algoritması Çalışıyor...")
            try:
                s, g = self._read_start_goal()
                t0 = time.perf_counter()
                out = astar(self.graph, s, g)
                t1 = time.perf_counter()
                ast_time = (t1 - t0) * 1000
                
                path = out.get("path", [])
                cost = out.get("cost")
                dlg.add_result(f"✅ A* Tamamlandı")
                dlg.add_result(f"  Başlangıç: {s}, Hedef: {g}")
                dlg.add_result(f"  Yol Uzunluğu: {len(path)}")
                dlg.add_result(f"  Yol: {' → '.join(map(str, path))}")
                dlg.add_result(f"  Toplam Maliyet: {cost:.6f}" if cost else "  Yol Bulunamamıştır!")
                dlg.add_result(f"  Çalışma Süresi: {ast_time:.4f} ms")
            except Exception as e:
                dlg.add_result(f"❌ A* Hatası: {str(e)}")

            dlg.add_separator()

            # Components Testi
            dlg.add_result(f"\n5️⃣  Connected Components Algoritması Çalışıyor...")
            try:
                t0 = time.perf_counter()
                comps = connected_components(self.graph)
                t1 = time.perf_counter()
                comp_time = (t1 - t0) * 1000
                
                dlg.add_result(f"✅ Connected Components Tamamlandı")
                dlg.add_result(f"  Bileşen Sayısı: {len(comps)}")
                for i, comp in enumerate(comps, 1):
                    dlg.add_result(f"  Bileşen {i}: {comp}")
                dlg.add_result(f"  Çalışma Süresi: {comp_time:.4f} ms")
            except Exception as e:
                dlg.add_result(f"❌ Components Hatası: {str(e)}")

            dlg.add_separator()

            # Centrality Testi
            dlg.add_result(f"\n6️⃣  Centrality Algoritması Çalışıyor...")
            try:
                t0 = time.perf_counter()
                deg = degree_centrality(self.graph)
                clo = closeness_centrality(self.graph)
                t1 = time.perf_counter()
                cent_time = (t1 - t0) * 1000
                
                top_deg = sorted(deg.items(), key=lambda x: x[1], reverse=True)[:5]
                top_clo = sorted(clo.items(), key=lambda x: x[1], reverse=True)[:5]
                
                dlg.add_result(f"✅ Centrality Tamamlandı")
                dlg.add_result(f"  Top 5 Degree Centrality:")
                for nid, v in top_deg:
                    dlg.add_result(f"    Düğüm {nid}: {v:.6f}")
                dlg.add_result(f"  Top 5 Closeness Centrality:")
                for nid, v in top_clo:
                    dlg.add_result(f"    Düğüm {nid}: {v:.6f}")
                dlg.add_result(f"  Çalışma Süresi: {cent_time:.4f} ms")
            except Exception as e:
                dlg.add_result(f"❌ Centrality Hatası: {str(e)}")

            dlg.add_separator()

            # Welsh-Powell Coloring Testi
            dlg.add_result(f"\n7️⃣  Welsh-Powell Renklendirme Algoritması Çalışıyor...")
            try:
                t0 = time.perf_counter()
                coloring = welsh_powell_coloring(self.graph)
                t1 = time.perf_counter()
                col_time = (t1 - t0) * 1000
                
                k = (max(coloring.values()) + 1) if coloring else 0
                dlg.add_result(f"✅ Welsh-Powell Tamamlandı")
                dlg.add_result(f"  Kullanılan Renk Sayısı: {k}")
                dlg.add_result(f"  Renkli Düğüm Sayısı: {len(coloring)}")
                dlg.add_result(f"  Çalışma Süresi: {col_time:.4f} ms")
            except Exception as e:
                dlg.add_result(f"❌ Welsh-Powell Hatası: {str(e)}")

            dlg.add_separator()
            dlg.add_result(f"\n✨ TÜM ALGORITMALAR BAŞARILI BİR ŞEKİLDE TEST EDİLDİ ✨")

            # Dialog'u göster
            dlg.exec()
            self.lbl.setText("Test işlemi tamamlandı.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def _make_random_graph(self, n: int, p: float) -> Graph:
        """
        n: node sayısı
        p: iki node arasında edge olma olasılığı (yoğunluğu kontrol eder)
        """
        g = Graph()

        # Node'lar
        for i in range(1, n + 1):
            node = Node(
                id=i,
                name=f"N{i}",
                aktiflik=random.random(),
                etkilesim=random.randint(0, 20),
                baglanti_sayisi=0,  # degree sonrası güncelleriz
            )
            # A* için (heuristic kullanıyorsan) koordinat ver
            node.x = random.uniform(-300, 300)
            node.y = random.uniform(-300, 300)
            g.add_node(node)

        # Edge'ler (yönsüz, duplicate yok)
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                if random.random() < p:
                    g.add_edge(i, j, weight_fn=WeightService.compute)

        # Node'ların bağlantı sayısını degree'e göre düzelt
        for nid in g.nodes:
            try:
                deg = len(list(g.neighbors(nid)))
            except Exception:
                # neighbors yoksa (çok düşük ihtimal) 0 geç
                deg = 0
            g.nodes[nid].baglanti_sayisi = deg

        # weight'leri bir daha hesapla (baglanti_sayisi update sonrası)
        g.recompute_all_weights(WeightService.compute)

        return g




    def stop_animation(self) -> None:
        if self._anim_timer.isActive():
            self._anim_timer.stop()
        self._anim_order = []
        self._anim_parent = {}
        self._anim_idx = 0
        self._anim_prev = None
        self._anim_last_edge_key = None

    def _reset_visual_states(self) -> None:
        # node reset
        for item in self.node_items.values():
            item.set_state("default")
        # edge reset
        for eitem in self.edge_items.values():
            if hasattr(eitem, "set_state"):
                eitem.set_state("default")

    def animate_traversal(self, order: list[int], parent: dict[int, int | None] | None = None, title: str = "Traversal") -> None:
        self.stop_animation()
        self._reset_visual_states()

        if not order:
            self.lbl.setText(f"{title}: gezilecek düğüm yok (order boş).")
            return

        self._anim_order = order
        self._anim_parent = parent or {}
        self._anim_idx = 0
        self._anim_prev = None
        self._anim_last_edge_key = None

        interval = int(self.sp_anim_ms.value()) if hasattr(self, "sp_anim_ms") else 250
        self.lbl.setText(f"{title} animasyonu başladı. Ziyaret sayısı: {len(order)}")
        self._anim_timer.start(interval)

    def _anim_step(self) -> None:
        if self._anim_idx >= len(self._anim_order):
            # bitti
            if self._anim_prev is not None and self._anim_prev in self.node_items:
                self.node_items[self._anim_prev].set_state("visited")
            self._anim_timer.stop()
            self.lbl.setText("Animasyon bitti.")
            return

        nid = self._anim_order[self._anim_idx]

        # önceki node visited olsun
        if self._anim_prev is not None and self._anim_prev in self.node_items:
            self.node_items[self._anim_prev].set_state("visited")

        # current node
        if nid in self.node_items:
            self.node_items[nid].set_state("current")
            # istersen kamerayı takip ettir:
            try:
                self.view.centerOn(self.node_items[nid])
            except Exception:
                pass

        # parent varsa: tree edge’i de highlight edelim (çok iyi durur)
        if nid in self._anim_parent:
            p = self._anim_parent.get(nid)
            if p is not None:
                key = undirected_key(p, nid)
                eitem = self.edge_items.get(key)
                if eitem and hasattr(eitem, "set_state"):
                    eitem.set_state("active")
                # önceki active edge'i visited yap
                if self._anim_last_edge_key and self._anim_last_edge_key in self.edge_items:
                    prev_e = self.edge_items[self._anim_last_edge_key]
                    if hasattr(prev_e, "set_state"):
                        prev_e.set_state("visited")
                self._anim_last_edge_key = key

        self._anim_prev = nid
        self._anim_idx += 1

    def make_random_graph_clicked(self) -> None:
        n = int(self.sp_test_n.value())
        p = float(self.sp_test_p.value())

        # model
        g = Graph()
        for i in range(1, n + 1):
            node = Node(
                id=i,
                name=f"N{i}",
                aktiflik=random.random(),
                etkilesim=random.randint(0, 20),
                baglanti_sayisi=0,
            )
            # A* için x/y (varsa kullanılır)
            node.x = random.uniform(-300, 300)
            node.y = random.uniform(-300, 300)
            g.add_node(node)

        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                if random.random() < p:
                    g.add_edge(i, j, weight_fn=WeightService.compute)

        # degree -> baglanti_sayisi
        for nid in g.nodes:
            deg = len(list(g.neighbors(nid)))
            g.nodes[nid].baglanti_sayisi = deg

        g.recompute_all_weights(WeightService.compute)

        # UI'ya bas
        self.graph = g
        self._render_graph()
        self._sync_edge_labels() if hasattr(self, "_sync_edge_labels") else None
        self.lbl.setText(f"Rastgele graf üretildi: n={n}, m={len(g.edges)}, p={p}")








    



