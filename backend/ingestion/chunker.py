from config import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text: str) ->list[str]:
    text = text.strip()

    if not text:
        return []

    sentences = _split_sentences(text)
    chunks = _build_chunks(sentences)

    return chunks

def _split_sentences(text: str) -> list[str]:
    import re
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]
 

def _build_chunks(sentences: list[str]) -> list[str]:

    chunks = []
    current_chunk = []
    current_len = 0
    i = 0

    while i < len(sentences):
        sentence = sentences[i]
        sentence_len = len(sentence)

        if current_len + sentence_len <= CHUNK_SIZE:
            current_chunk.append(sentence)
            current_len += sentence_len + 1
            i+= 1
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                while current_chunk and current_len > CHUNK_OVERLAP:
                    removed = current_chunk.pop(0)
                    current_len -= len(removed) + 1
            else:
                chunks.append(sentence)
                current_chunk = []
                current_len = 0
                i += 1
 
    if current_chunk:
        chunks.append(" ".join(current_chunk))
 
    return chunks

