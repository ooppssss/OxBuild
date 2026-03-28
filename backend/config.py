import os 
from dotenv import load_dotenv
import openai

load_dotenv()

OXLO_API_KEY   = os.getenv("API_KEY")
OXLO_BASE_URL  = "https://api.oxlo.ai/v1"
 
# ── Shared OpenAI-compatible client (used by all modules) ────────────────────
# One client instance, imported wherever an Oxlo call is needed.
oxlo_client = openai.OpenAI(
    base_url=OXLO_BASE_URL,
    api_key=OXLO_API_KEY,
)
 

MODEL_EXTRACT = "deepseek-v3.2"
MODEL_RESOLVE = "deepseek-v3.2"
MODEL_INFER = "deepseek-r1-8b"
MODEL_QUERY = "mistral-7b"

CHUNK_SIZE = 400
CHUNK_OVERLAP = 80

RELATION_VOCAB = [
    "works_at",
    "founded_by",
    "acquired_by",
    "competitor_of",
    "related_to",
    "part_of",
    "located_in",
    "created_by",
    "uses_technology",
    "invested_in",
    "collaborated_with",
]
 
RELATION_VOCAB_STR = ", ".join(RELATION_VOCAB)  