from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

class GraphView(QGraphicsView):
    nodeSelected = Signal(int)  # node_id

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHints(self.renderHints())
        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.scene.selectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self) -> None:
        items = self.scene.selectedItems()
        if not items:
            return
        item = items[0]
        if hasattr(item, "node_id"):
            self.nodeSelected.emit(int(item.node_id))
