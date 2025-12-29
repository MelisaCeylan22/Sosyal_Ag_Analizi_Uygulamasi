from __future__ import annotations

from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsItem,
)
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtCore import QPointF


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, node_id: int, label: str = "", radius: float = 18.0):
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.node_id = node_id
        self.radius = radius
        self._edges: list["EdgeItem"] = []

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # default görünüm
        self._pen_normal = QPen(QColor(30, 30, 30), 1)
        self._brush_normal = QBrush(QColor(245, 245, 245))
        self.setPen(self._pen_normal)
        self.setBrush(self._brush_normal)

        # highlight görünüm
        self._pen_high = QPen(QColor(255, 140, 0), 3)
        self._brush_high = QBrush(QColor(255, 255, 200))

        self.text = QGraphicsTextItem(label, self)
        self.text.setPos(-radius, -radius - 18)

    def set_label(self, s: str) -> None:
        self.text.setPlainText(s)

    def set_highlight(self, on: bool) -> None:
        if on:
            self.setPen(self._pen_high)
            self.setBrush(self._brush_high)
        else:
            self.setPen(self._pen_normal)
            self.setBrush(self._brush_normal)

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
        self.setZValue(-1)  # çizgiler node’un arkasında

        a.add_edge(self)
        b.add_edge(self)

        # default görünüm
        self._pen_normal = QPen(QColor(70, 70, 70), 1)
        self.setPen(self._pen_normal)

        # highlight görünüm
        self._pen_high = QPen(QColor(220, 20, 60), 3)

        # weight etiketi (edge ortasında)
        self.text = QGraphicsTextItem("", self)
        self.text.setDefaultTextColor(QColor(20, 20, 20))
        self.text.setZValue(0)

        self._weight = None
        if weight is not None:
            self.set_weight(weight)

        self.update_position()

    def set_highlight(self, on: bool) -> None:
        self.setPen(self._pen_high if on else self._pen_normal)

    def set_weight(self, w: float) -> None:
        self._weight = float(w)
        self.text.setPlainText(f"{self._weight:.4f}")
        self._update_text_pos()

    def _update_text_pos(self) -> None:
        p1 = self.a.scenePos()
        p2 = self.b.scenePos()
        mid = (p1 + p2) / 2
        # yazıyı biraz yukarı kaydır (çizginin üstünde dursun)
        self.text.setPos(mid.x() + 6, mid.y() - 16)

    def update_position(self) -> None:
        p1 = self.a.scenePos()
        p2 = self.b.scenePos()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())
        self._update_text_pos()
