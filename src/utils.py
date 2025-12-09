# src/utils.py
import pdfplumber
from PIL import Image
import pytesseract
import io
from typing import List, Tuple

def read_pdf_text(path: str) -> str:
    """
    Robust reader:
    - If file is PDF → attempt pdfplumber
    - If pdfplumber fails → fallback to OCR or plain text
    - If file is NOT a PDF → read as plain text
    """

    import os

    # Detect extension
    ext = os.path.splitext(path)[1].lower()

    # If not PDF → read as plain text
    if ext != ".pdf":
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            return ""

    # If PDF → try pdfplumber
    import pdfplumber
    pages_text = []

    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                try:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)
                    else:
                        # If page empty: OCR fallback
                        pil_img = page.to_image(resolution=300).original
                        ocr_text = pytesseract.image_to_string(pil_img)
                        pages_text.append(ocr_text)
                except Exception:
                    continue
        return "\n".join(pages_text)

    except Exception:
        # Last fallback → read file as text
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except:
            return ""


def normalize_amount(raw: str):
    """
    Convert strings like '₹12,345', '$12,345.50', '12,345' to integer rupee-like units (rounded).
    Returns int or None.
    """
    if not raw:
        return None
    # remove common currency symbols and words
    import re
    r = re.sub(r'[^\d\.\-]', '', raw)
    if r == "":
        return None
    try:
        val = float(r)
        return int(round(val))
    except Exception:
        return None

def split_lines(text: str) -> List[str]:
    if not text:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]
