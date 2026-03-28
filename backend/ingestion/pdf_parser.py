import fitz  # PyMuPDF


def extract_text_from_pdf(raw_bytes: bytes) -> str:
    """
    Takes raw PDF bytes (from FastAPI UploadFile.read()),
    returns a single cleaned string of all text across all pages.
    """
    text_parts = []

    with fitz.open(stream=raw_bytes, filetype="pdf") as doc:
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text("text")   # plain text mode
            if page_text.strip():
                # tag each page so source_text anchors can reference page number
                text_parts.append(f"[Page {page_num}]\n{page_text.strip()}")

    full_text = "\n\n".join(text_parts)
    return _clean_text(full_text)


def _clean_text(text: str) -> str:
    """
    Remove excessive whitespace and fix common PDF extraction artifacts.
    """
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        # drop lines that are just page numbers or single characters
        if len(line) <= 2:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)