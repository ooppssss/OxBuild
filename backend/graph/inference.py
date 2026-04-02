import json
from config import oxlo_client, MODEL_INFER
from graph.store import graph_store
from models import InferenceResult
import asyncio


# ── Main function ─────────────────────────────────────────────────────────────

async def generate_insights() -> list[InferenceResult]:
    """
    Analyses the current graph and uses deepseek-r1-8b (chain-of-thought)
    to surface non-obvious connections between entities from DIFFERENT documents.

    The "killer feature" — finds links a human would likely miss when
    reading the documents separately.
    """
    if len(graph_store.nodes) < 2:
        return []

    # Build a compact graph summary to send to the model
    graph_summary = _build_graph_summary()

    if not graph_summary["cross_doc_pairs"]:
        return []

    response = await asyncio.to_thread(
        oxlo_client.chat.completions.create,
        model=MODEL_INFER,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": _build_user_prompt(graph_summary)},
        ],
        temperature=0.0,
        max_tokens=3000,
    )

    raw = response.choices[0].message.content
    return _parse_response(raw)


# ── Graph summary builder ─────────────────────────────────────────────────────

def _build_graph_summary() -> dict:
    """
    Builds a compact representation of the graph for the inference prompt.

    Finds entity pairs that:
    - Appear in DIFFERENT documents (cross-doc)
    - Are not already directly connected
    - Share at least one common neighbour (2nd-degree connection)

    These are the best candidates for hidden link discovery.
    """
    nodes = graph_store.get_all_nodes()
    edges = graph_store.get_all_edges()

    # map node_id → set of doc_ids it appears in
    node_docs: dict[str, set[str]] = {
        n.id: set(n.doc_ids) for n in nodes
    }

    # map node_id → set of directly connected node_ids
    direct_connections: dict[str, set[str]] = {}
    for edge in edges:
        src = edge.source.lower()
        tgt = edge.target.lower()
        direct_connections.setdefault(src, set()).add(tgt)
        direct_connections.setdefault(tgt, set()).add(src)

    # find cross-doc pairs with shared neighbours but no direct link
    cross_doc_pairs = []
    node_ids = list(node_docs.keys())

    for i in range(len(node_ids)):
        for j in range(i + 1, len(node_ids)):
            a, b = node_ids[i], node_ids[j]

            # must be from different documents
            if node_docs[a] & node_docs[b]:
                continue  # share a doc — skip

            # must not already be directly connected
            if b in direct_connections.get(a, set()):
                continue

            # must share at least one common neighbour
            neighbours_a = direct_connections.get(a, set())
            neighbours_b = direct_connections.get(b, set())
            shared = neighbours_a & neighbours_b

            if shared:
                cross_doc_pairs.append({
                    "entity_a": graph_store.nodes[a].label,
                    "entity_b": graph_store.nodes[b].label,
                    "doc_a": list(node_docs[a]),
                    "doc_b": list(node_docs[b]),
                    "shared_neighbours": [
                        graph_store.nodes[s].label
                        for s in shared
                        if s in graph_store.nodes
                    ],
                })

    # existing edges as context for the model
    edge_summary = [
        {
            "source": e.source,
            "relation": e.relation,
            "target": e.target,
            "doc_id": e.doc_id,
        }
        for e in edges[:80]   # cap at 80 to stay within token budget
    ]

    return {
        "cross_doc_pairs": cross_doc_pairs[:10],   # top 10 candidates
        "existing_edges": edge_summary,
    }


# ── Prompt ────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are an expert knowledge graph analyst with strong reasoning skills.

You will receive:
1. A list of entity pairs from DIFFERENT documents that share common neighbours but have no direct connection.
2. The existing edges in the graph for context.

Your task: For each candidate pair, reason carefully about whether a meaningful hidden relationship exists.
Use chain-of-thought reasoning to justify your conclusion.

Only suggest a link if you are reasonably confident it is meaningful and non-obvious.
Do NOT suggest trivial or generic links.

Return ONLY a valid JSON array. No markdown, no explanation outside the JSON.

Output format:
[
  {
    "from_entity": "Entity A",
    "to_entity": "Entity B",
    "suggested_relation": "one of the relation types",
    "reasoning": "step-by-step explanation of why this link likely exists",
    "confidence": "high | medium | low"
  }
]

If no meaningful hidden links exist, return: []
"""


def _build_user_prompt(summary: dict) -> str:
    return f"""Analyse these cross-document entity pairs for hidden connections:

CANDIDATE PAIRS (from different documents, sharing common neighbours):
{json.dumps(summary["cross_doc_pairs"], indent=2)}

EXISTING GRAPH EDGES (for context):
{json.dumps(summary["existing_edges"], indent=2)}

Find non-obvious meaningful links. Return only the JSON array."""


# ── Parser ────────────────────────────────────────────────────────────────────

def _parse_response(raw: str) -> list[InferenceResult]:
    cleaned = raw.strip()

    # strip markdown fences
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"[Inference] JSON parse failed.\nRaw:\n{raw[:300]}")
        return []

    if not isinstance(data, list):
        return []

    results = []
    for item in data:
        if not all(
            isinstance(item.get(k), str) and item[k].strip()
            for k in ("from_entity", "to_entity", "suggested_relation", "reasoning", "confidence")
        ):
            continue

        results.append(InferenceResult(
            from_entity=item["from_entity"].strip(),
            to_entity=item["to_entity"].strip(),
            suggested_relation=item["suggested_relation"].strip(),
            reasoning=item["reasoning"].strip(),
            confidence=item["confidence"].strip().lower(),
        ))

    return results