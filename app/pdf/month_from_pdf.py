from __future__ import annotations
import re
import fitz  # PyMuPDF

MONTH_MAP = {
    "JANUARY": 1, "FEBRUARY": 2, "MARCH": 3, "APRIL": 4, "MAY": 5, "JUNE": 6,
    "JULY": 7, "AUGUST": 8, "SEPTEMBER": 9, "OCTOBER": 10, "NOVEMBER": 11, "DECEMBER": 12
}

# 예: "MAY ㅣ 05" 또는 "MAY | 05" 둘 다 대응
MONTH_RE = re.compile(r"\b(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\b.*?(\d{2})")

def extract_month_number(pdf_path: str, page_index: int) -> int:
    doc = fitz.open(pdf_path)
    text = doc.load_page(page_index).get_text("text").upper()
    m = MONTH_RE.search(text)
    if not m:
        raise ValueError(f"Cannot find month header on page {page_index+1}")
    month_name = m.group(1)
    return MONTH_MAP[month_name]
