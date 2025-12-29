from __future__ import annotations
from typing import Dict, List
from .base import neighbors


def welsh_powell_coloring(graph) -> Dict[int, int]:
    nodes = list(getattr(graph, "nodes", {}).keys())
    # dereceye göre azalan sırala
    nodes.sort(key=lambda x: len(list(neighbors(graph, x))), reverse=True)

    color: Dict[int, int] = {}
    current_color = 0

    for u in nodes:
        if u in color:
            continue
        color[u] = current_color

        for v in nodes:
            if v in color:
                continue
            # v’nin aynı renge boyanması için komşularında bu renk olmamalı
            ok = True
            for nb in neighbors(graph, v):
                if color.get(nb) == current_color:
                    ok = False
                    break
            if ok:
                color[v] = current_color

        current_color += 1

    return color
