from collections import deque

from config import oxlo_client, MODEL_QUERY
from graph.store import graph_store
from models import QueryResponse, GraphData, Node, Edge
import asyncio


# ── Main function ─────────────────────────────────────────────────────────────

async def multihop_query(query: str, depth: int = 2) -> QueryResponse:
    """
    1. Parse the natural language query → canonical entity name (via Oxlo)
    2. BFS from that entity up to `depth` hops
    3. Return the subgraph of all visited nodes + edges
    """
    # Step 1 — resolve query to an entity name
    entity = await _parse_query_to_entity(query)

    # Step 2 — check entity exists in graph
    start_node = graph_store.get_node(entity)
    if start_node is None:
        # fuzzy fallback: try partial match
        entity = _fuzzy_match(entity)
        start_node = graph_store.get_node(entity)

    if start_node is None:
        return QueryResponse(
            entity=entity,
            depth=depth,
            subgraph=GraphData(nodes=[], edges=[]),
        )

    # Step 3 — BFS traversal
    visited_node_ids, visited_edges = _bfs(entity, depth)

    # Step 4 — collect subgraph
    nodes = [graph_store.nodes[nid] for nid in visited_node_ids if nid in graph_store.nodes]
    edges = visited_edges

    return QueryResponse(
        entity=start_node.label,
        depth=depth,
        subgraph=GraphData(nodes=nodes, edges=edges),
    )


# ── NL query parser ───────────────────────────────────────────────────────────

async def _parse_query_to_entity(query: str) -> str:
    """
    Uses Oxlo (mistral-7b) to extract the primary entity name from a
    natural language question.

    e.g. "who founded Tesla?" → "Tesla"
         "what does Elon Musk do?" → "Elon Musk"
         "Tesla" → "Tesla"
    """
    # if query looks like a plain entity already, skip the API call
    if len(query.split()) <= 3 and "?" not in query:
        return query.strip()

    response = await asyncio.to_thread(
        oxlo_client.chat.completions.create,
        model=MODEL_QUERY,
        messages=[
            {
                "role": "system",
                "content": (
                    "You extract the single most important entity name from a question. "
                    "Reply with ONLY the entity name — no explanation, no punctuation, "
                    "no extra words. Example: 'who founded Tesla?' → 'Tesla'"
                ),
            },
            {"role": "user", "content": query},
        ],
        temperature=0.0,
        max_tokens=20,
    )

    entity = response.choices[0].message.content.strip()
    return entity


# ── BFS ───────────────────────────────────────────────────────────────────────

def _bfs(start: str, depth: int) -> tuple[set[str], list[Edge]]:
    """
    Breadth-first search from `start` node up to `depth` hops.

    Returns:
        visited_node_ids — set of all node ids reached
        visited_edges    — list of all edges traversed

    Why BFS and not DFS?
    BFS guarantees we find the shortest path connections first.
    For a "show me 2nd degree connections" feature this is exactly right —
    we want all nodes at hop 1 before exploring hop 2.
    """
    start_id = start.lower()
    visited_node_ids: set[str] = {start_id}
    visited_edges: list[Edge] = []
    seen_edge_keys: set[tuple] = set()

    # queue holds (node_id, current_depth)
    queue: deque[tuple[str, int]] = deque()
    queue.append((start_id, 0))

    while queue:
        current_id, current_depth = queue.popleft()

        if current_depth >= depth:
            continue

        for edge in graph_store.get_neighbours(current_id):
            edge_key = (edge.source.lower(), edge.relation, edge.target.lower())
            if edge_key not in seen_edge_keys:
                seen_edge_keys.add(edge_key)
                visited_edges.append(edge)

            neighbour_id = edge.target.lower()
            if neighbour_id not in visited_node_ids:
                visited_node_ids.add(neighbour_id)
                queue.append((neighbour_id, current_depth + 1))

    return visited_node_ids, visited_edges


# ── Fuzzy match fallback ──────────────────────────────────────────────────────

def _fuzzy_match(query: str) -> str:
    """
    If exact node lookup fails, find the node whose label contains
    the query string (case-insensitive). Returns query unchanged if
    no match found.
    """
    query_lower = query.lower()
    for node_id, node in graph_store.nodes.items():
        if query_lower in node_id or query_lower in node.label.lower():
            return node.label
    return query