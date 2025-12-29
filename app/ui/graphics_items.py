from __future__ import annotations

from PySide6.QtWidgets import (
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsItem,
)
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRectF, QPointF


class NodeItem(QGraphicsItem):
    """Custom node item that draws a stylized person icon instead of a plain circle.

    Keeps the same public API as before: `set_label`, `set_state`, `add_edge`, and
    `itemChange` behavior for edge position updates.
    """
    def __init__(self, node_id: int, label: str = "", radius: float = 18.0):
        super().__init__()
        self.node_id = node_id
        self.radius = radius
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

        # runtime brush/pen used for painting
        self._current_brush = self._brush_default
        self._current_pen = self._pen_default

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
            self._current_brush = self._brush_visited
            self._current_pen = self._pen_default
        elif state == "current":
            self._current_brush = self._brush_current
            self._current_pen = self._pen_current
        elif state == "start":
            self._current_brush = self._brush_start
            self._current_pen = self._pen_current
        elif state == "goal":
            self._current_brush = self._brush_goal
            self._current_pen = self._pen_current
        else:
            self._current_brush = self._brush_default
            self._current_pen = self._pen_default

        self.update()

    def set_color(self, color_index: int) -> None:
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
            "#F7DC6F", "#BB8FCE", "#85C1E9", "#F8B88B", "#ABEBC6",
        ]
        color = colors[color_index % len(colors)]
        self._current_brush = QBrush(QColor(color))
        self._current_pen = QPen(Qt.black, 2)
        self.update()

    def boundingRect(self) -> QRectF:
        r = self.radius
        return QRectF(-r - 4, -r - 20, 2 * r + 8, 2 * r + 40)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        r = self.radius
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self._current_pen)
        painter.setBrush(self._current_brush)

        # draw head
        head_r = r * 0.38
        head_center = QPointF(0, -r * 0.5)
        painter.drawEllipse(head_center, head_r, head_r)

        # draw body (rounded rect)
        body_w = r * 0.9
        body_h = r * 1.0
        body_rect = QRectF(-body_w / 2, -r * 0.1, body_w, body_h)
        path = QPainterPath()
        path.addRoundedRect(body_rect, r * 0.2, r * 0.2)
        painter.drawPath(path)

        # arms (simple lines)
        arm_y = -r * 0.0
        painter.drawLine(QPointF(-body_w / 2, arm_y), QPointF(body_w / 2, arm_y))

        # legs (two lines)
        leg_y0 = body_rect.bottom()
        painter.drawLine(QPointF(-body_w / 4, leg_y0), QPointF(-body_w / 4, leg_y0 + r * 0.6))
        painter.drawLine(QPointF(body_w / 4, leg_y0), QPointF(body_w / 4, leg_y0 + r * 0.6))

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
