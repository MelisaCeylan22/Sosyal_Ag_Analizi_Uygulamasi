from __future__ import annotations
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem

class NodeItem(QGraphicsEllipseItem):
    def __init__(self, node_id: int, label: str = "", radius: float = 18.0):
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.node_id = node_id
        self._edges: list["EdgeItem"] = []

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self.text = QGraphicsTextItem(label, self)
        self.text.setPos(-radius, -radius - 18)

    def set_label(self, s: str) -> None:
        self.text.setPlainText(s)

    def add_edge(self, e: "EdgeItem") -> None:
        self._edges.append(e)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for e in self._edges:
                e.update_position()
        return super().itemChange(change, value)

class EdgeItem(QGraphicsLineItem):
    def __init__(self, a: NodeItem, b: NodeItem):
        super().__init__()
        self.a = a
        self.b = b
        self.setZValue(-1)  # çizgiler node’un arkasında
        a.add_edge(self)
        b.add_edge(self)
        self.update_position()

    def update_position(self) -> None:
        p1 = self.a.scenePos()
        p2 = self.b.scenePos()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())
