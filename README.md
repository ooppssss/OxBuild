# GraphMind — Structured Intelligence System

> Built for **OxBuild Hackathon by Oxlo.ai**

GraphMind transforms unstructured documents into a live, queryable knowledge graph. Instead of keyword search or basic RAG, it maps the **DNA of your data** — extracting entities, resolving them across documents, and revealing hidden connections a human would likely miss.

---

## The Problem

Information is trapped in messy paragraphs. RAG systems retrieve text chunks but cannot reason about *structure* — who is connected to what, and why. GraphMind solves this by building a permanent, structured memory from your documents.

---

## Demo

**Paste two documents → watch the graph build → discover hidden cross-document links**

![GraphMind Demo](./assets/demo.png)

---

## Features

### Two-Pass Extraction
- **Pass 1** — `deepseek-v3.2` reads each text chunk and extracts raw entity relationship triplets, along with the exact source sentence that proves each relationship
- **Pass 2** — `deepseek-v3.2` resolves entities across all chunks (`"Elon"` + `"Mr. Musk"` → `"Elon Musk"`), normalises relation labels into a fixed vocabulary, and deduplicates

### Contextual Anchoring
Every edge in the graph stores the original sentence that created it. Click any connection in the graph to see exactly which sentence in the source document produced that link — solving the black box problem of AI extraction.

### Multi-Hop Graph Traversal
Query the graph with natural language. Ask about `"Tesla"` and the system returns Tesla, everything connected to Tesla, and everything connected to *those* entities — surfacing second-degree connections automatically.

### Cross-Document Inference
After ingesting multiple documents, the inference engine (`deepseek-r1-8b`) analyses entities that appear in different documents, share common neighbours, but have no direct connection. It uses chain-of-thought reasoning to suggest meaningful hidden links with a confidence score.

### Interactive Force Graph
Nodes bounce and connect in a live force-directed graph. Cross-document entities glow pink. Particles flow along edges. Click any edge to see the source excerpt.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + react-force-graph-2d |
| Backend | FastAPI (Python) |
| PDF parsing | PyMuPDF |
| OCR | Tesseract + Pillow |
| AI models | Oxlo.ai API (OpenAI-compatible) |
| Graph store | In-memory adjacency list |

---

## Models Used (via Oxlo.ai)

| Model | Role |
|---|---|
| `deepseek-v3.2` | Pass 1 triplet extraction + Pass 2 entity/relation normalisation |
| `deepseek-r1-8b` | Cross-document inference engine (chain-of-thought) |
| `mistral-7b` | Natural language query parsing |

---

## Project Structure

```
graphmind/
├── backend/
│   ├── main.py               # FastAPI app + all routes
│   ├── config.py             # Oxlo client, models, relation vocab
│   ├── models.py             # Pydantic schemas
│   ├── ingestion/
│   │   ├── pdf_parser.py     # PDF → text (PyMuPDF)
│   │   ├── ocr_parser.py     # Image → text (Tesseract)
│   │   └── chunker.py        # Overlapping text chunks
│   ├── extraction/
│   │   ├── pass1.py          # Raw triplet extraction via Oxlo
│   │   └── pass2.py          # Entity resolution + normalisation via Oxlo
│   └── graph/
│       ├── store.py          # In-memory adjacency list
│       ├── traversal.py      # BFS multi-hop query
│       └── inference.py      # Cross-doc hidden link discovery
└── frontend/
    └── src/
        ├── App.jsx
        └── components/
            ├── TextInput.jsx
            ├── FileInput.jsx
            ├── GraphCanvas.jsx
            └── InsightsPanel.jsx
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Tesseract OCR installed system-wide
  - Mac: `brew install tesseract`
  - Ubuntu: `sudo apt install tesseract-ocr`
  - Windows: [installer](https://github.com/UB-Mannheim/tesseract/wiki)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in the `backend/` folder:

```
OXLO_API_KEY=your_oxlo_api_key_here
```

Start the server:

```bash
python -m uvicorn main:app --reload
```

API runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ingest/text` | Ingest plain text |
| `POST` | `/ingest/pdf` | Ingest PDF file |
| `POST` | `/ingest/image` | Ingest image (OCR) |
| `GET` | `/query?q=Tesla&depth=2` | Multi-hop graph query |
| `GET` | `/inference` | Cross-doc hidden link discovery |
| `GET` | `/graph` | Full graph state |
| `DELETE` | `/graph` | Clear graph |

---

## How It Works

```
Document (PDF / Image / Text)
        ↓
   Text Extraction
        ↓
  Overlapping Chunks
        ↓
  Pass 1 — deepseek-v3.2
  Extract raw (Source, Relation, Target) + source_text
        ↓
  Pass 2 — deepseek-v3.2
  Resolve entities + normalise relations + deduplicate
        ↓
  Adjacency List Graph Store
        ↓
  ┌─────────────────────────────────┐
  │  Multi-hop BFS Query            │
  │  Cross-doc Inference Engine     │
  │  Interactive Force Graph UI     │
  └─────────────────────────────────┘
```

---

## Relation Vocabulary

All extracted relations are normalised into one of:

`works_at` · `founded_by` · `acquired_by` · `competitor_of` · `related_to` · `part_of` · `located_in` · `created_by` · `uses_technology` · `invested_in` · `collaborated_with`

---

## Registered Oxlo.ai Email

`your_registered_email@example.com`

---

## License

MIT
