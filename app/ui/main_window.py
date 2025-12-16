from __future__ import annotations
import time

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QGroupBox, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt

from app.ui.graph_view import GraphView
from app.ui.graphics_items import NodeItem, EdgeItem

from app.core.graph import Graph
from app.core.node import Node
from app.core.weight_service import WeightService

from app.algorithms.bfs import BFS
from app.algorithms.dfs import DFS
from app.algorithms.dijkstra import Dijkstra

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sosyal Ağ Analizi - PySide6")
        self.resize(1100, 700)

        self.graph = Graph()
        self.view = GraphView()
        self.view.nodeSelected.connect(self.on_node_selected)

        # UI Item index
        self.node_items: dict[int, NodeItem] = {}
        self.edge_items: dict[tuple[int,int], EdgeItem] = {}

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

        # Node form
        g1 = QGroupBox("Node İşlemleri")
        f1 = QFormLayout(g1)
        self.in_node_id = QLineEdit()
        self.in_node_name = QLineEdit()
        self.in_aktiflik = QLineEdit("0.0")
        self.in_etkilesim = QLineEdit("0.0")
        self.in_baglanti = QLineEdit("0")

        f1.addRow("ID", self.in_node_id)
        f1.addRow("Name", self.in_node_name)
        f1.addRow("Aktiflik", self.in_aktiflik)
        f1.addRow("Etkileşim", self.in_etkilesim)
        f1.addRow("Bağl. Sayısı", self.in_baglanti)

        btn_add = QPushButton("Node Ekle")
        btn_add.clicked.connect(self.add_node_clicked)
        f1.addRow(btn_add)

        # Edge form
        g2 = QGroupBox("Edge İşlemleri")
        f2 = QFormLayout(g2)
        self.in_u = QLineEdit()
        self.in_v = QLineEdit()
        f2.addRow("U", self.in_u)
        f2.addRow("V", self.in_v)
        btn_edge = QPushButton("Edge Ekle (Ağırlık Otomatik)")
        btn_edge.clicked.connect(self.add_edge_clicked)
        f2.addRow(btn_edge)

        # Algo buttons
        g3 = QGroupBox("Algoritmalar (Demo)")
        f3 = QFormLayout(g3)
        self.in_start = QLineEdit()
        self.in_goal = QLineEdit()
        f3.addRow("Start", self.in_start)
        f3.addRow("Goal", self.in_goal)

        btn_bfs = QPushButton("BFS")
        btn_bfs.clicked.connect(self.run_bfs)
        btn_dfs = QPushButton("DFS")
        btn_dfs.clicked.connect(self.run_dfs)
        btn_dij = QPushButton("Dijkstra")
        btn_dij.clicked.connect(self.run_dijkstra)

        f3.addRow(btn_bfs)
        f3.addRow(btn_dfs)
        f3.addRow(btn_dij)

        # Results table
        self.lbl_status = QLabel("Hazır.")
        self.tbl = QTableWidget(0, 2)
        self.tbl.setHorizontalHeaderLabels(["Key", "Value"])

        lay.addWidget(g1)
        lay.addWidget(g2)
        lay.addWidget(g3)
        lay.addWidget(self.lbl_status)
        lay.addWidget(self.tbl)
        lay.addStretch(1)
        return panel

    # ---------------- Demo seed ----------------
    def _seed_demo(self) -> None:
        # 3 node ekleyelim
        self._add_node_model_and_ui(Node(1, "A", 0.8, 12, 3, x=0, y=0), x=-120, y=-40)
        self._add_node_model_and_ui(Node(2, "B", 0.4, 5, 2, x=0, y=0), x=40, y=-60)
        self._add_node_model_and_ui(Node(3, "C", 0.6, 9, 4, x=0, y=0), x=0, y=90)

        # 2 edge
        self._add_edge_model_and_ui(1, 2)
        self._add_edge_model_and_ui(2, 3)

    # ---------------- UI callbacks ----------------
    def on_node_selected(self, node_id: int) -> None:
        n = self.graph.nodes.get(node_id)
        if not n:
            return
        self.in_node_id.setText(str(n.id))
        self.in_node_name.setText(n.name)
        self.in_aktiflik.setText(str(n.aktiflik))
        self.in_etkilesim.setText(str(n.etkilesim))
        self.in_baglanti.setText(str(n.baglanti_sayisi))

    def add_node_clicked(self) -> None:
        nid = int(self.in_node_id.text().strip())
        node = Node(
            id=nid,
            name=self.in_node_name.text().strip(),
            aktiflik=float(self.in_aktiflik.text().strip()),
            etkilesim=float(self.in_etkilesim.text().strip()),
            baglanti_sayisi=int(self.in_baglanti.text().strip()),
        )
        self._add_node_model_and_ui(node, x=0, y=0)

    def add_edge_clicked(self) -> None:
        u = int(self.in_u.text().strip())
        v = int(self.in_v.text().strip())
        self._add_edge_model_and_ui(u, v)

    # ---------------- Model+UI helpers ----------------
    def _add_node_model_and_ui(self, node: Node, x: float, y: float) -> None:
        self.graph.add_node(node)
        item = NodeItem(node.id)
        item.setPos(x, y)
        self.view.scene.addItem(item)
        self.node_items[node.id] = item

    def _add_edge_model_and_ui(self, u: int, v: int) -> None:
        # Model
        self.graph.add_edge(u, v, weight_fn=WeightService.compute)
        # UI
        key = (u, v) if u < v else (v, u)
        a = self.node_items[key[0]]
        b = self.node_items[key[1]]
        eitem = EdgeItem(a, b)
        self.view.scene.addItem(eitem)
        self.edge_items[key] = eitem

    # ---------------- Algorithm runners (demo) ----------------
    def _show_result(self, title: str, data: dict) -> None:
        self.tbl.setRowCount(0)
        for k, v in data.items():
            r = self.tbl.rowCount()
            self.tbl.insertRow(r)
            self.tbl.setItem(r, 0, QTableWidgetItem(str(k)))
            self.tbl.setItem(r, 1, QTableWidgetItem(str(v)))
        self.lbl_status.setText(f"{title} tamamlandı.")

    def run_bfs(self) -> None:
        start = int(self.in_start.text().strip())
        t0 = time.perf_counter()
        res = BFS().run(self.graph, start=start)
        dt = (time.perf_counter() - t0) * 1000
        self._show_result(res.name, {**res.payload, "ms": round(dt, 3)})

    def run_dfs(self) -> None:
        start = int(self.in_start.text().strip())
        t0 = time.perf_counter()
        res = DFS().run(self.graph, start=start)
        dt = (time.perf_counter() - t0) * 1000
        self._show_result(res.name, {**res.payload, "ms": round(dt, 3)})

    def run_dijkstra(self) -> None:
        start = int(self.in_start.text().strip())
        goal = int(self.in_goal.text().strip())
        t0 = time.perf_counter()
        res = Dijkstra().run(self.graph, start=start, goal=goal)
        dt = (time.perf_counter() - t0) * 1000
        self._show_result(res.name, {**res.payload, "ms": round(dt, 3)})
