from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Qt


class TestDialog(QDialog):
    """
    Algoritmaların test sonuçlarını adım adım gösteren dialog.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Algoritma Test Sonuçları")
        self.resize(700, 600)

        layout = QVBoxLayout(self)

        # Başlık
        self.title_label = QLabel("Algoritma Test Sonuçları")
        layout.addWidget(self.title_label)

        # Sonuçları gösteren text edit
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("font-family: Courier New; font-size: 10pt;")
        layout.addWidget(self.result_text)

        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def add_result(self, text: str) -> None:
        """Sonuç metnine bir satır ekle"""
        current = self.result_text.toPlainText()
        if current:
            self.result_text.setPlainText(current + "\n" + text)
        else:
            self.result_text.setPlainText(text)
        # Son satırı görünür yap (scroll to end)
        cursor = self.result_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.result_text.setTextCursor(cursor)

    def clear_results(self) -> None:
        """Sonuçları temizle"""
        self.result_text.clear()

    def add_separator(self) -> None:
        """Ayırıcı çizgi ekle"""
        self.add_result("=" * 80)
