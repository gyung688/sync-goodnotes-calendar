from __future__ import annotations
import json
import os
import re

from app.core.calendar_grid import Cell, cell_to_day
from app.pdf.month_from_pdf import extract_month_number
from app.llm.ollama_parser import parse_events_ollama
from app.common.text_filter import is_meaningful_text
from app.calendar.google_provider import GoogleCalendarProvider, stable_ical_uid
from app.calendar.mapper import google_event_from_extracted

CELL_RE = re.compile(r"cell_r(\d)_c(\d)\.png$", re.IGNORECASE)
GOOGLE_CALENDAR_ID = "primary"
TZ = "America/Vancouver"

google = GoogleCalendarProvider(
    credentials_path="secrets/google_credentials.json",
    token_path="secrets/google_token.json",
)

def load_ocr_map(ocr_json_path: str) -> dict[str, str]:
    with open(ocr_json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def iter_cells_from_paths(ocr_map: dict[str, str]):
    for path, text in ocr_map.items():
        m = CELL_RE.search(path.replace("\\", "/"))
        if not m:
            continue
        r, c = int(m.group(1)), int(m.group(2))
        yield Cell(r=r, c=c), (text or "").strip(), path

def main():
    # ====== Environment ======
    PDF_PATH = "input/2026.pdf"
    PAGE_INDEX = 32   # 0-based (“31페이지”면 32가 월간 캘린더였던 케이스)
    YEAR = 2026
    OCR_JSON = "out/ocr/page_033.json"  # OCR 결과
    # OLLAMA_MODEL = "qwen2.5:7b"
    OLLAMA_MODEL = "llama3.1:8b"
    # =====================================

    month = extract_month_number(PDF_PATH, PAGE_INDEX)
    ocr_map = load_ocr_map(OCR_JSON)

    counter = 0
    all_events = []
    for cell, text, src_path in iter_cells_from_paths(ocr_map):
        if not text:
            continue

        if not is_meaningful_text(text):
            continue

        day = cell_to_day(YEAR, month, cell)
        if day is None:
            continue

        counter += 1
        print(f'=========={counter}=={day}===========')
        parsed = parse_events_ollama(OLLAMA_MODEL, YEAR, month, day, text)
        for ev in parsed.get("events", []):
            if not ev.get("title"):
                continue
            # if ev.get("confidence", 0) < 0.3:
            #     continue
            ev["_source_cell"] = {"r": cell.r, "c": cell.c, "img": src_path}
            all_events.append(ev)

    os.makedirs("out/events", exist_ok=True)
    out_path = f"out/events/{YEAR}-{month:02d}_page{PAGE_INDEX+1}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"events": all_events}, f, ensure_ascii=False, indent=2)

    print("Saved:", out_path)
    print("Events:", len(all_events))

    for ev in all_events:
        title = (ev.get("title") or "").strip()
        if not title:
            continue
        if ev.get("confidence", 0) < 0.35:
            continue

        src = ev["_source_cell"]
        #  중복 방지 키: year-month-day + title + (time) + source cell
        key = f"{ev['start']}|{ev.get('end')}|{title}|r{src['r']}c{src['c']}"
        ical = stable_ical_uid(key)

        body = google_event_from_extracted(ev, TZ, ical_uid=ical)
        google.upsert_event(GOOGLE_CALENDAR_ID, body)

if __name__ == "__main__":
    main()