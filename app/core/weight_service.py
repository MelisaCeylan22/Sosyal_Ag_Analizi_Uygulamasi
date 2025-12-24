from __future__ import annotations
from dataclasses import dataclass
from app.core.node import Node

@dataclass(slots=True)
class WeightParams:
    a: float = 1.0
    b: float = 1.0
    c: float = 1.0

class WeightService:
    params = WeightParams()

    @staticmethod
    def compute(n1: Node, n2: Node) -> float:
        da = (n1.aktiflik - n2.aktiflik) ** 2
        de = (n1.etkilesim - n2.etkilesim) ** 2
        db = (n1.baglanti_sayisi - n2.baglanti_sayisi) ** 2
        p = WeightService.params
        return 1.0 / (1.0 + p.a * da + p.b * de + p.c * db)
