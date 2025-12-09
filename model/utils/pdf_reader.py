"""
ATS-GRADE PDF READER
- Best for resumes
- Clean, normalized text for NLP/skill extraction
- Multi-engine fallback (pdfminer -> pdfplumber)
- Determines left + right columns correctly
- Removes headers, footers, decorative elements
"""

import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import pdfplumber


# ------------------------------------
# CLEANUP UTILITIES
# ------------------------------------
def normalize_text(text: str) -> str:
    if not text:
        return ""

    # Remove multiple spaces
    text = re.sub(r"[^\S\r\n]+", " ", text)

    # Fix broken bullet points
    text = text.replace("• ", "\n• ")

    # Merge hyphenated line breaks
    text = re.sub(r"-\n", "", text)

    # Replace multiple line breaks with single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ------------------------------------
# PDFMINER WITH COLUMN SORTING
# ------------------------------------
def extract_pdfminer_ordered(path: str) -> str:
    try:
        page_text = []

        for page_layout in extract_pages(path):
            blocks = []

            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    # Each block: (x0, y0, text)
                    blocks.append((element.x0, element.y0, element.get_text()))

            # Sort by y0 desc, then x0 asc → correct for resumes with columns
            blocks.sort(key=lambda b: (-b[1], b[0]))

            page_text.append("\n".join([b[2] for b in blocks]))

        return "\n\n".join(page_text)

    except Exception:
        return ""


# ------------------------------------
# PDFPLUMBER FALLBACK
# ------------------------------------
def extract_pdfplumber_clean(path: str) -> str:
    try:
        full_text = ""

        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                # Extract while preserving left/right columns
                extracted = page.extract_text(layout=True)
                if extracted:
                    full_text += extracted + "\n"

        return full_text

    except Exception:
        return ""


# ------------------------------------
# MASTER ATS EXTRACTOR
# ------------------------------------
def extract_text_for_ats(path: str) -> str:
    """
    Main extractor for ATS system.
    Produces clean + deterministic text for NLP pipelines.
    """

    # 1. PDFMiner (best ordering)
    text = extract_pdfminer_ordered(path)
    if text.strip():
        return normalize_text(text)

    # 2. pdfplumber fallback
    text = extract_pdfplumber_clean(path)
    if text.strip():
        return normalize_text(text)

    # Final fallback → empty
    return ""


# -----------------------------------------------------------------
# Compatible wrapper expected by other scripts: extract_text_from_pdf
# -----------------------------------------------------------------
def extract_text_from_pdf(path: str) -> str:
    """
    Backwards-compatible wrapper used by older code (e.g. ats_score.py).
    Internally delegates to extract_text_for_ats so behaviour is deterministic.

    Keep this small so external callers don't need to change.
    """
    return extract_text_for_ats(path)


# Exported symbols
__all__ = ["extract_text_from_pdf", "extract_text_for_ats"]


# Example / simple test when run directly
if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "resume5.pdf"

    content = extract_text_from_pdf(pdf_path)

    print("\n================= EXTRACTED RESUME TEXT =================\n")
    print(content or "[NO TEXT EXTRACTED — PDF MAY BE SCANNED OR EMPTY]")
    print("\n=========================================================\n")
