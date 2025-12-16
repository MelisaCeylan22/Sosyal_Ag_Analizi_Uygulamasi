from __future__ import annotations
from app.core.node import Node

class WeightService:
    @staticmethod
    def compute(a: Node, b: Node) -> float:
        da = (a.aktiflik - b.aktiflik) ** 2
        de = (a.etkilesim - b.etkilesim) ** 2
        db = (a.baglanti_sayisi - b.baglanti_sayisi) ** 2
        return 1.0 / (1.0 + da + de + db)
