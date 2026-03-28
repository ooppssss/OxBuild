import io 
import platform 
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"   
    )

def extract_text_from_image(raw_bytes: bytes) -> str:

    image = Image.open(io.BytesIO(raw_bytes))
    image = _preprocess(iamge)
    text = pytesseract.image_to_string(image, lang = "eng")
    return _clean_text(text)

def _preprocess(Image: Image.Image) -> Image.Image:
    image = image.convert("L")

    image = image.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    width, height = image.size
    if width < 1000:
        scale = 1000 / width
        image = image.resize(
            (int(width * scale), int(height * scale)),
            Image.LANCZOS,
        )
 
    return image

def _clean_text(text: str) -> str:
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()

        if (len(line)) <= 2:
            continue

        cleaned.append(line)

    return "\n".join(cleaned)