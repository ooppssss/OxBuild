# GraphMind — Structured Intelligence System

> Built for **OxBuild Hackathon by Oxlo.ai**

GraphMind transforms unstructured documents into a live, queryable knowledge graph. Instead of keyword search or basic RAG, it maps the **DNA of your data** — extracting entities, resolving them across documents, and revealing hidden connections a human would likely miss.

---

## The Problem

Information is trapped in messy paragraphs. RAG systems retrieve text chunks but cannot reason about *structure* — who is connected to what, and why. GraphMind solves this by building a permanent, structured memory from your documents.

---

## Demo

**Paste two documents → watch the graph build → discover hidden cross-document links**
✅ Backend live: https://oxbuild.onrender.com
✅ Frontend live: https://graphmindfrontend.vercel.app

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

## Demo 

Example 1:
doc_ai_companies: `OpenAI was founded by Sam Altman, Elon Musk, and Greg Brockman in San Francisco in 2015. OpenAI developed GPT-4, which is one of the most powerful large language models in the world. Microsoft invested over 10 billion dollars in OpenAI and integrated OpenAI technology into its Bing search engine and Azure cloud platform. Sam Altman serves as the CEO of OpenAI and previously led Y Combinator, the famous startup accelerator based in San Francisco. Elon Musk later left the OpenAI board and founded xAI, his own artificial intelligence company. xAI developed Grok, a large language model that competes directly with GPT-4. Tesla, also led by Elon Musk, uses deep learning and artificial intelligence for its Full Self Driving system. Andrej Karpathy was the Director of AI at Tesla and later joined OpenAI as a researcher before leaving to start his own AI education company. Google DeepMind was formed by the merger of Google Brain and DeepMind and is headquartered in London. DeepMind developed AlphaFold, which solved the protein folding problem and revolutionized biological research. Google invested heavily in Anthropic, an AI safety company founded by Dario Amodei and Daniela Amodei, who were former OpenAI employees. Anthropic developed Claude, an AI assistant that competes with ChatGPT developed by OpenAI. Meta AI is the artificial intelligence research division of Meta, led by Yann LeCun, who is a pioneer in deep learning and convolutional neural networks. Meta released LLaMA, an open source large language model that researchers around the world use freely. Nvidia supplies the GPU hardware that powers almost every major AI company including OpenAI, Google, Meta, and Anthropic. Jensen Huang founded Nvidia and serves as its CEO, making Nvidia one of the most valuable companies in the world due to the AI boom.`

doc_tech_startups: `Sam Altman invested in Stripe, the payments company founded by Patrick Collison and John Collison in San Francisco. Stripe is used by millions of businesses worldwide and is one of the most valuable private companies in the world. Y Combinator, previously run by Sam Altman, has funded companies like Airbnb, Dropbox, and Reddit. Airbnb was founded by Brian Chesky and is headquartered in San Francisco. Peter Thiel co-founded PayPal along with Elon Musk and later founded Palantir, a data analytics company used by governments and intelligence agencies. Palantir uses artificial intelligence and machine learning for its data analysis platforms. Peter Thiel also invested early in Facebook, which later became Meta. Sequoia Capital is a venture capital firm that invested in Apple, Google, and OpenAI. Andreessen Horowitz, also known as a16z, invested in OpenAI, Airbnb, and many other major tech companies. Jensen Huang is on the board of several AI startups and has partnerships with Microsoft and Google for GPU supply agreements. Elon Musk acquired Twitter and rebranded it as X, aiming to turn it into an everything app. X competes with Meta platforms including Instagram and Facebook in the social media space.`

<img width="625" height="738" alt="Screenshot 2026-04-02 at 15 05 41" src="https://github.com/user-attachments/assets/9ba70b55-0844-45bf-b062-297e7ceef2de" />


Example 2:
doc_space: `NASA launched the Artemis mission to send humans back to the Moon. SpaceX is providing the rocket technology for the Artemis mission. Elon Musk founded SpaceX in 2002 in Hawthorne, California.`

doc_cars: `Tesla makes electric cars and is headquartered in Austin, Texas. Elon Musk is the CEO of Tesla. Ford and Tesla compete in the electric vehicle market.`


---

## Registered Oxlo.ai Email

`nrsamrit@gmail.com`

---

## License

MIT
