from __future__ import annotations

import mysql.connector

from app.core.graph import Graph
from app.core.node import Node
from app.core.edge import undirected_key
from app.core import mysql_config


class MySqlStorageService:
    @staticmethod
    def _connect():
        return mysql.connector.connect(
            host=mysql_config.HOST,
            port=mysql_config.PORT,
            user=mysql_config.USER,
            password=mysql_config.PASSWORD,
            database=mysql_config.DATABASE,
        )

    @staticmethod
    def save_graph(graph: Graph, graph_id: int = 1, name: str = "SocialGraph") -> None:
        con = MySqlStorageService._connect()
        try:
            cur = con.cursor()
            con.start_transaction()

            # graph upsert
            cur.execute(
                "INSERT INTO graphs(graph_id, name) VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE name=VALUES(name)",
                (graph_id, name),
            )

            # aynı graph_id için temizle
            cur.execute("DELETE FROM edges WHERE graph_id=%s", (graph_id,))
            cur.execute("DELETE FROM nodes WHERE graph_id=%s", (graph_id,))

            # nodes insert
            for nid, n in graph.nodes.items():
                cur.execute(
                    """
                    INSERT INTO nodes(graph_id, node_id, name, aktiflik, etkilesim, baglanti_sayisi, x, y)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        graph_id,
                        int(nid),
                        str(getattr(n, "name", "")),
                        float(getattr(n, "aktiflik", 0.0)),
                        float(getattr(n, "etkilesim", 0.0)),
                        int(getattr(n, "baglanti_sayisi", 0)),
                        float(getattr(n, "x", 0.0)),
                        float(getattr(n, "y", 0.0)),
                    ),
                )

            # edges insert (yönsüz -> key sıralı)
            for (u, v), e in graph.edges.items():
                uu, vv = undirected_key(int(u), int(v))  # min,max
                cur.execute(
                    """
                    INSERT INTO edges(graph_id, u_id, v_id, weight)
                    VALUES (%s,%s,%s,%s)
                    """,
                    (graph_id, uu, vv, float(getattr(e, "weight", 1.0))),
                )

            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    @staticmethod
    def load_graph(graph_id: int = 1) -> Graph:
        con = MySqlStorageService._connect()
        try:
            cur = con.cursor()

            g = Graph()

            cur.execute(
                """
                SELECT node_id, name, aktiflik, etkilesim, baglanti_sayisi, x, y
                FROM nodes
                WHERE graph_id=%s
                """,
                (graph_id,),
            )
            for node_id, name, aktiflik, etkilesim, baglanti, x, y in cur.fetchall():
                n = Node(int(node_id), str(name), float(aktiflik), float(etkilesim), int(baglanti))
                setattr(n, "x", float(x))
                setattr(n, "y", float(y))
                g.add_node(n)

            cur.execute(
                """
                SELECT u_id, v_id, weight
                FROM edges
                WHERE graph_id=%s
                """,
                (graph_id,),
            )
            for u, v, w in cur.fetchall():
                # weight direkt DB'den
                g.add_edge(int(u), int(v), weight=float(w))

            return g
        finally:
            con.close()
