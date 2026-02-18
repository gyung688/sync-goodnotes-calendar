import re
import fitz  # PyMuPDF

# The header contains month names (e.g., MAY | 05 / JANUARY | 01)
MONTH_RE = re.compile(
    r"\b(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\b"
)

# The header contains day of week names (e.g., SUN | MON | TUE | WED | THU | FRI | SAT)
DOW_RE = re.compile(r"\bSUN\b.*\bMON\b.*\bTUE\b.*\bWED\b.*\bTHU\b.*\bFRI\b.*\bSAT\b", re.DOTALL)


def is_monthly_calendar_page(text_upper: str) -> bool:
    """
    Template signature-based detection:
    - Month names in the header
    - Day of week headers
    """
    return bool(MONTH_RE.search(text_upper) and DOW_RE.search(text_upper))

def find_monthly_calendar_pages(pdf_path: str) -> list[int]:
    doc = fitz.open(pdf_path)
    hits: list[int] = []
    for i in range(doc.page_count):
        text = doc.load_page(i).get_text("text").upper()
        if is_monthly_calendar_page(text):
            hits.append(i)  # 0-based page index
    return hits
