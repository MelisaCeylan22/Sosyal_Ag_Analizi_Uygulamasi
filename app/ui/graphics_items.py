from __future__ import annotations

from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsItem,
)
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtCore import Qt


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, node_id: int, label: str = "", radius: float = 18.0):
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.node_id = node_id
        self._edges: list["EdgeItem"] = []

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self._pen_default = QPen(Qt.black, 1)
        self._pen_current = QPen(QColor("#111111"), 2)

        self._brush_default = QBrush(QColor("#F2F2F2"))
        self._brush_visited = QBrush(QColor("#B7F7C6"))
        self._brush_current = QBrush(QColor("#FFE27A"))
        self._brush_start = QBrush(QColor("#A8D8FF"))
        self._brush_goal = QBrush(QColor("#FFB3B3"))

        self.setPen(self._pen_default)
        self.setBrush(self._brush_default)

        self.text = QGraphicsTextItem(label, self)
        self.text.setDefaultTextColor(QColor("#111111"))
        self.text.setPos(-radius, -radius - 18)

    def set_label(self, s: str) -> None:
        self.text.setPlainText(s)

    def set_color(self, color_index: int) -> None:
        """
        Renklendirme algoritması için düğüme renk ata.
        color_index: 0-9 arası renk numarası
        """
        colors = [
            "#FF6B6B",  # 0: Kırmızı
            "#4ECDC4",  # 1: Turkuaz
            "#45B7D1",  # 2: Mavi
            "#FFA07A",  # 3: Salmon
            "#98D8C8",  # 4: Mint
            "#F7DC6F",  # 5: Sarı
            "#BB8FCE",  # 6: Mor
            "#85C1E9",  # 7: Açık Mavi
            "#F8B88B",  # 8: Turuncu
            "#ABEBC6",  # 9: Açık Yeşil
        ]
        color = colors[color_index % len(colors)]
        self.setBrush(QBrush(QColor(color)))
        self.setPen(QPen(Qt.black, 2))

    def set_state(self, state: str) -> None:
        # state: default | visited | current | start | goal
        if state == "visited":
            self.setBrush(self._brush_visited)
            self.setPen(self._pen_default)
        elif state == "current":
            self.setBrush(self._brush_current)
            self.setPen(self._pen_current)
        elif state == "start":
            self.setBrush(self._brush_start)
            self.setPen(self._pen_current)
        elif state == "goal":
            self.setBrush(self._brush_goal)
            self.setPen(self._pen_current)
        else:
            self.setBrush(self._brush_default)
            self.setPen(self._pen_default)

    def add_edge(self, e: "EdgeItem") -> None:
        self._edges.append(e)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for e in self._edges:
                e.update_position()
        return super().itemChange(change, value)


class EdgeItem(QGraphicsLineItem):
    def __init__(self, a: NodeItem, b: NodeItem, weight: float | None = None):
        super().__init__()
        self.a = a
        self.b = b
        self.setZValue(-1)

        self._pen_default = QPen(QColor("#666666"), 1)
        self._pen_active = QPen(QColor("#E53935"), 2)
        self._pen_visited = QPen(QColor("#2E7D32"), 2)

        self.setPen(self._pen_default)

        self.weight_text = QGraphicsTextItem("", self)
        self.weight_text.setDefaultTextColor(QColor("#111111"))

        a.add_edge(self)
        b.add_edge(self)

        if weight is not None:
            self.set_weight(weight)

        self.update_position()

    def set_weight(self, w: float) -> None:
        self.weight_text.setPlainText(f"{w:.3f}")
        self.update_position()

    def set_state(self, state: str) -> None:
        # state: default | active | visited
        if state == "active":
            self.setPen(self._pen_active)
        elif state == "visited":
            self.setPen(self._pen_visited)
        else:
            self.setPen(self._pen_default)

    def update_position(self) -> None:
        p1 = self.a.scenePos()
        p2 = self.b.scenePos()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())

        # weight label ortada
        mx = (p1.x() + p2.x()) / 2
        my = (p1.y() + p2.y()) / 2
        self.weight_text.setPos(mx, my)
