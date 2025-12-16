from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class Node:
    id: int
    name: str = ""
    aktiflik: float = 0.0
    etkilesim: float = 0.0
    baglanti_sayisi: int = 0

    # UI için konum (A* heuristic istersen kullanırsın)
    x: float = 0.0
    y: float = 0.0
