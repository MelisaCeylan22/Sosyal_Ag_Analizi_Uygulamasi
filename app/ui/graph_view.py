from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtGui import QPainter, QBrush
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt

class GraphView(QGraphicsView):
    nodeSelected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setRenderHint(QPainter.Antialiasing, True)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setBackgroundBrush(QBrush(Qt.white))

        self.scene.selectionChanged.connect(self._on_sel_changed)

    def _on_sel_changed(self) -> None:
        items = self.scene.selectedItems()
        if not items:
            return
        it = items[0]
        if hasattr(it, "node_id"):
            self.nodeSelected.emit(int(it.node_id))
