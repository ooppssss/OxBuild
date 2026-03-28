from collections import defaultdict
from models import Node, Edge, GraphData, RawTriplet


class GraphStore:
    """
    In-memory knowledge graph using an adjacency list.

    Structure:
        nodes  — dict[node_id → Node]
        edges  — list[Edge]
        adj    — dict[node_id → list[Edge]]   (outgoing edges per node)

    Why adjacency list over a plain edge list?
    Multi-hop traversal needs to find all neighbours of a node instantly.
    With a plain list you'd scan every edge on every hop — O(E) per hop.
    With an adjacency list it's O(degree) — much faster for graph queries.
    """

    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self.adj: dict[str, list[Edge]] = defaultdict(list)

    # ── Write ─────────────────────────────────────────────────────────────────

    def add_triplets(self, triplets: list[RawTriplet]) -> None:
        """
        Adds a list of normalised triplets to the graph.
        Automatically merges nodes that already exist.
        """
        for t in triplets:
            self._upsert_node(t.source, t.doc_id)
            self._upsert_node(t.target, t.doc_id)

            edge = Edge(
                source=t.source,
                target=t.target,
                relation=t.relation,
                source_text=t.source_text,
                doc_id=t.doc_id,
            )

            # avoid duplicate edges
            if not self._edge_exists(t.source, t.relation, t.target):
                self.edges.append(edge)
                self.adj[t.source].append(edge)

    def _upsert_node(self, name: str, doc_id: str) -> None:
        """
        Inserts a new node or merges doc_id into an existing one.
        Node id is the lowercase version for consistent lookup;
        label preserves original casing for display.
        """
        node_id = name.lower()
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(
                id=node_id,
                label=name,
                doc_ids=[doc_id],
            )
        else:
            # merge doc reference if not already tracked
            if doc_id not in self.nodes[node_id].doc_ids:
                self.nodes[node_id].doc_ids.append(doc_id)

    def _edge_exists(self, source: str, relation: str, target: str) -> bool:
        source_id = source.lower()
        for edge in self.adj.get(source_id, []):
            if (
                edge.relation == relation
                and edge.target.lower() == target.lower()
            ):
                return True
        return False

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_node(self, name: str) -> Node | None:
        return self.nodes.get(name.lower())

    def get_neighbours(self, name: str) -> list[Edge]:
        """Returns all outgoing edges from a node."""
        return self.adj.get(name.lower(), [])

    def get_all_nodes(self) -> list[Node]:
        return list(self.nodes.values())

    def get_all_edges(self) -> list[Edge]:
        return self.edges

    def to_graph_data(self) -> GraphData:
        return GraphData(
            nodes=self.get_all_nodes(),
            edges=self.get_all_edges(),
        )

    # ── Utility ───────────────────────────────────────────────────────────────

    def clear(self) -> None:
        self.nodes.clear()
        self.edges.clear()
        self.adj.clear()

    def __len__(self) -> int:
        return len(self.nodes)


# ── Singleton ─────────────────────────────────────────────────────────────────
# One shared instance across the entire FastAPI app lifecycle.
# All routes import this directly.
graph_store = GraphStore()