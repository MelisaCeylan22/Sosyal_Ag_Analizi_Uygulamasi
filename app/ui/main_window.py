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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Social Graph - PySide6 (Dynamic Weight + I/O)")
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

        layout = QVBoxLayout(root)
        layout.addWidget(splitter)

        self._seed_demo()

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        lay = QVBoxLayout(panel)

        # ---- Node form ----
        g1 = QGroupBox("Node CRUD")
        f1 = QFormLayout(g1)
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

        f1.addRow(btn_add)
        f1.addRow(btn_upd)
        f1.addRow(btn_del)

        # ---- Edge form ----
        g2 = QGroupBox("Edge CRUD")
        f2 = QFormLayout(g2)
        self.in_u = QLineEdit()
        self.in_v = QLineEdit()
        f2.addRow("U", self.in_u)
        f2.addRow("V", self.in_v)

        btn_eadd = QPushButton("Edge Ekle (weight auto)")
        btn_eadd.clicked.connect(self.add_edge_clicked)
        btn_edel = QPushButton("Edge Sil")
        btn_edel.clicked.connect(self.delete_edge_clicked)
        f2.addRow(btn_eadd)
        f2.addRow(btn_edel)

        # ---- Weight formülü (Dinamik) ----
        gW = QGroupBox("Weight Formülü (katsayılar)")
        fW = QFormLayout(gW)

        self.in_a = QLineEdit(str(WeightService.params.a))
        self.in_b = QLineEdit(str(WeightService.params.b))
        self.in_c = QLineEdit(str(WeightService.params.c))

        fW.addRow("a (aktiflik)", self.in_a)
        fW.addRow("b (etkileşim)", self.in_b)
        fW.addRow("c (bağlantı)", self.in_c)

        btn_w_update = QPushButton("Tüm Edge Weight'lerini Güncelle")
        btn_w_update.clicked.connect(self.update_weights_clicked)
        fW.addRow(btn_w_update)

        btn_w_show = QPushButton("Edge Weight'lerini Göster")
        btn_w_show.clicked.connect(self.show_weights_clicked)
        fW.addRow(btn_w_show)

        # ---- File I/O ----
        g3 = QGroupBox("Dosya (JSON/CSV) + Çıktılar")
        f3 = QFormLayout(g3)

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

        f3.addRow(btn_csv_load)
        f3.addRow(btn_csv_save)
        f3.addRow(btn_json_load)
        f3.addRow(btn_json_save)
        f3.addRow(btn_adj_list)
        f3.addRow(btn_adj_mat)

        self.lbl = QLabel("Hazır.")

        lay.addWidget(g1)
        lay.addWidget(g2)
        lay.addWidget(gW)
        lay.addWidget(g3)
        lay.addWidget(self.lbl)
        lay.addStretch(1)
        return panel

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
            self.lbl.setText(f"Weight güncellendi.")
        except Exception as e:
            self.lbl.setText(f"Hata (weight): {e}")

    def show_weights_clicked(self) -> None:
        if not self.graph.edges:
            QMessageBox.information(self, "Edge Weights", "(Edge yok)")
            return
        lines = [f"{u}-{v}   w={e.weight:.6f}" for (u, v), e in sorted(self.graph.edges.items())]
        QMessageBox.information(self, "Edge Weights", "\n".join(lines))

    # ---------- File handlers (HATAYI FIXLEYEN KISIM: BU FONKSIYONLAR CLASS ICINDE) ----------
    def csv_load_clicked(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "CSV Seç", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            self.graph = StorageService.load_csv(path)
            self.graph.recompute_all_weights(WeightService.compute)
            self._render_graph()
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
        ids, mat = StorageService.adjacency_matrix(self.graph)
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
            eit = EdgeItem(a, b)
            self.view.scene.addItem(eit)
            self.edge_items[key] = eit

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
        eit = EdgeItem(a, b)
        self.view.scene.addItem(eit)
        self.edge_items[key] = eit
        return e

    def _remove_edge(self, u: int, v: int) -> None:
        key = undirected_key(u, v)
        self.graph.remove_edge(u, v)
        eit = self.edge_items.pop(key, None)
        if eit:
            self.view.scene.removeItem(eit)
