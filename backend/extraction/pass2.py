import json
from config import oxlo_client, MODEL_RESOLVE, RELATION_VOCAB_STR
from models import RawTriplet
import asyncio


# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert knowledge graph normaliser.
You will receive a list of raw relationship triplets extracted from one or more documents.
Clean and normalise them in three ways:

1. ENTITY RESOLUTION
   - Merge entities that refer to the same real-world thing into one canonical name.
   - Examples:
       "Elon", "Mr. Musk", "Elon Musk CEO"  →  "Elon Musk"
       "Tesla Inc", "Tesla", "TSLA"          →  "Tesla"
   - Always prefer the most complete and formal version of the name.

2. RELATION NORMALISATION
   - Map every relation to the closest match from this vocabulary:
     {VOCAB}
   - Examples:
       "founded"         →  "founded_by"
       "was started by"  →  "founded_by"
       "competes with"   →  "competitor_of"
       "works for"       →  "works_at"
       "uses"            →  "uses_technology"
   - If nothing fits, use "related_to" as fallback.

3. DEDUPLICATION
   - Remove triplets that have the same source, relation, and target after normalisation.
   - Keep the first occurrence, discard duplicates.

Return ONLY a valid JSON array. No explanation, no markdown.

Output format:
[
  {
    "source": "Canonical Entity A",
    "relation": "normalised_relation",
    "target": "Canonical Entity B",
    "source_text": "original sentence kept as-is",
    "doc_id": "original doc_id kept as-is"
  }
]
"""


def _build_user_prompt(triplets: list[RawTriplet]) -> str:
    triplets_list = [
        {
            "source":      t.source,
            "relation":    t.relation,
            "target":      t.target,
            "source_text": t.source_text,
            "doc_id":      t.doc_id,
        }
        for t in triplets
    ]
    return f"Normalise the following triplets:\n\n{json.dumps(triplets_list, indent=2)}\n\nReturn only the cleaned JSON array."


# ── Main function ─────────────────────────────────────────────────────────────

  # add this at the top

async def resolve_and_normalise(triplets: list[RawTriplet]) -> list[RawTriplet]:
    if not triplets:
        return []

    system = SYSTEM_PROMPT.replace("{VOCAB}", RELATION_VOCAB_STR)
    
    print(f"[Pass2] Sending {len(triplets)} triplets to Oxlo for normalisation...")

    response = await asyncio.to_thread(
        oxlo_client.chat.completions.create,
        model=MODEL_RESOLVE,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": _build_user_prompt(triplets)},
        ],
        temperature=0.0,
        max_tokens=3000,
    )

    print(f"[Pass2] Normalisation complete")
    raw = response.choices[0].message.content
    return _parse_response(raw, triplets)

# ── Parser ────────────────────────────────────────────────────────────────────

def _parse_response(raw: str, original: list[RawTriplet]) -> list[RawTriplet]:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"[Pass2] JSON parse failed. Falling back to raw triplets.\nRaw:\n{raw[:300]}")
        return original   # never lose data

    if not isinstance(data, list):
        return original

    result = []
    seen = set()

    for item in data:
        if not all(
            isinstance(item.get(k), str) and item[k].strip()
            for k in ("source", "relation", "target", "source_text", "doc_id")
        ):
            continue

        key = (
            item["source"].strip().lower(),
            item["relation"].strip().lower(),
            item["target"].strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)

        result.append(RawTriplet(
            source=item["source"].strip(),
            relation=item["relation"].strip(),
            target=item["target"].strip(),
            source_text=item["source_text"].strip(),
            doc_id=item["doc_id"].strip(),
        ))

    # if model returned garbage, fall back to originals
    return result if result else original