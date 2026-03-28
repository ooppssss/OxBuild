import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import OXLO_API_KEY
from models import (
    TextIngestRequest, IngestResponse,
    QueryResponse, InferenceResponse, GraphData
)
from graph.store import graph_store
from ingestion.pdf_parser import extract_text_from_pdf
from ingestion.ocr_parser import extract_text_from_image
from ingestion.chunker import chunk_text
from extraction.pass1 import extract_triplets
from extraction.pass2 import resolve_and_normalise
from graph.traversal import multihop_query
from graph.inference import generate_insights

# ── Sanity check ─────────────────────────────────────────────────────────────
if not OXLO_API_KEY:
    raise RuntimeError("OXLO_API_KEY not found. Check your .env file.")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="GraphMind API",
    description="Structured Intelligence System — transforms documents into a queryable knowledge graph.",
    version="1.0.0",
)

# ── CORS (allow React dev server) ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "message": "GraphMind is running"}


# ── Ingest: plain text ────────────────────────────────────────────────────────
@app.post("/ingest/text", response_model=IngestResponse)
async def ingest_text(body: TextIngestRequest):
    doc_id = body.doc_id or f"doc_{uuid.uuid4().hex[:8]}"
    return await _process_text(body.text, doc_id)


# ── Ingest: PDF ───────────────────────────────────────────────────────────────
@app.post("/ingest/pdf", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    raw_bytes = await file.read()
    text = extract_text_from_pdf(raw_bytes)
    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from PDF.")
    return await _process_text(text, doc_id)


# ── Ingest: image (OCR) ───────────────────────────────────────────────────────
@app.post("/ingest/image", response_model=IngestResponse)
async def ingest_image(file: UploadFile = File(...)):
    allowed = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only PNG/JPEG/WEBP images are accepted.")
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    raw_bytes = await file.read()
    text = extract_text_from_image(raw_bytes)
    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from image.")
    return await _process_text(text, doc_id)


# ── Query: multi-hop graph traversal ─────────────────────────────────────────
@app.get("/query", response_model=QueryResponse)
async def query(q: str, depth: int = 2):
    """
    q     — natural language or entity name  e.g. "Tesla" or "who founded Tesla"
    depth — how many hops to traverse (default 2)
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    depth = max(1, min(depth, 3))   # clamp between 1 and 3
    result = await multihop_query(q, depth)
    return result


# ── Inference: cross-doc hidden links ────────────────────────────────────────
@app.get("/inference", response_model=InferenceResponse)
async def inference():
    """
    Analyses the current graph and surfaces non-obvious connections
    across different documents.
    """
    insights = await generate_insights()
    return InferenceResponse(insights=insights)


# ── Graph: return full current state ─────────────────────────────────────────
@app.get("/graph", response_model=GraphData)
def get_graph():
    return graph_store.to_graph_data()


# ── Graph: clear everything ───────────────────────────────────────────────────
@app.delete("/graph")
def clear_graph():
    graph_store.clear()
    return {"status": "cleared"}


# ── Shared processing pipeline ───────────────────────────────────────────────
async def _process_text(text: str, doc_id: str) -> IngestResponse:
    """
    Shared pipeline used by all three ingest endpoints.
    text → chunk → pass1 → pass2 → store → response
    """
    chunks = chunk_text(text)

    # Pass 1 — extract raw triplets from every chunk
    raw_triplets = []
    for chunk in chunks:
        triplets = await extract_triplets(chunk, doc_id)
        raw_triplets.extend(triplets)

    # Pass 2 — resolve entities + normalise relations across ALL triplets
    clean_triplets = await resolve_and_normalise(raw_triplets)

    # Store into graph
    nodes_before = len(graph_store.nodes)
    edges_before = len(graph_store.edges)
    graph_store.add_triplets(clean_triplets)
    nodes_after  = len(graph_store.nodes)
    edges_after  = len(graph_store.edges)

    return IngestResponse(
        doc_id=doc_id,
        chunks_processed=len(chunks),
        triplets_extracted=len(raw_triplets),
        nodes_added=nodes_after - nodes_before,
        edges_added=edges_after - edges_before,
        graph=graph_store.to_graph_data(),
    )