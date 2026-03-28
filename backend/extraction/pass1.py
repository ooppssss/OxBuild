import json
from config import oxlo_client, MODEL_EXTRACT
from models import RawTriplet


# ── Prompts ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a precise knowledge graph extractor.
Your job is to read a text chunk and extract every meaningful relationship between named entities.

Rules:
- Only extract relationships explicitly stated or very strongly implied in the text.
- Each entity must be a specific named person, company, technology, place, or concept.
- Do NOT extract vague entities like "the company" or "someone".
- Copy the exact sentence from the text that supports the relationship into source_text.
- Return ONLY a valid JSON array. No explanation, no markdown, no extra text.

Output format:
[
  {
    "source": "Entity A",
    "relation": "relationship description",
    "target": "Entity B",
    "source_text": "exact sentence from the text that proves this relationship"
  }
]

If no clear relationships exist, return an empty array: []
"""


def _build_user_prompt(chunk: str) -> str:
    return f"""Extract all entity relationships from the following text:

---
{chunk}
---

Return only the JSON array."""


# ── Main function ─────────────────────────────────────────────────────────────

async def extract_triplets(chunk: str, doc_id: str) -> list[RawTriplet]:
    """
    Pass 1 — sends a text chunk to Oxlo and returns raw triplets.
    """
    response = oxlo_client.chat.completions.create(
        model=MODEL_EXTRACT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": _build_user_prompt(chunk)},
        ],
        temperature=0.1,
        max_tokens=1500,
    )

    raw = response.choices[0].message.content
    return _parse_response(raw, doc_id)


# ── Parser ────────────────────────────────────────────────────────────────────

def _parse_response(raw: str, doc_id: str) -> list[RawTriplet]:
    cleaned = raw.strip()

    # strip markdown fences if model wrapped output
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"[Pass1] JSON parse failed for doc {doc_id}. Raw:\n{raw[:300]}")
        return []

    if not isinstance(data, list):
        return []

    triplets = []
    for item in data:
        if not all(
            isinstance(item.get(k), str) and item[k].strip()
            for k in ("source", "relation", "target", "source_text")
        ):
            continue
        triplets.append(RawTriplet(
            source=item["source"].strip(),
            relation=item["relation"].strip(),
            target=item["target"].strip(),
            source_text=item["source_text"].strip(),
            doc_id=doc_id,
        ))

    return triplets