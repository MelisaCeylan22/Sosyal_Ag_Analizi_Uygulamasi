from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.core.graph import Graph

@dataclass(slots=True)
class AlgoResult:
    name: str
    payload: Any

class Algorithm(ABC):
    @abstractmethod
    def run(self, graph: Graph, **params) -> AlgoResult:
        raise NotImplementedError
