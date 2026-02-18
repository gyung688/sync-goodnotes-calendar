import re

def is_meaningful_text(text: str) -> bool:
    if not text:
        return False

    t = text.strip()

    # Too short
    if len(t) < 2:
        return False

    # When the text is purely numeric, it's likely a date or page number, not an event title
    if re.fullmatch(r"\d+", t):
        return False

    # When the text is only special characters
    if re.fullmatch(r"[^\w가-힣]+", t):
        return False

    return True
