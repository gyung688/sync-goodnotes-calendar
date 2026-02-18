from __future__ import annotations
import json
import re
import requests

def parse_events_ollama(
    model: str,
    year: int,
    month: int,
    day: int,
    text: str,
    tz: str = "America/Vancouver",
) -> dict:
    """
    Returns dict: {"events":[...]}  (events can be empty)
    """
    iso_date = f"{year:04d}-{month:02d}-{day:02d}"
    prompt = f"""
                You extract calendar events from OCR text written inside a monthly planner cell.

                Return ONLY valid JSON.
                ABSOLUTELY NO explanations, comments, markdown, or text outside the JSON.
                Do NOT include code fences like ```json or ```.

                Schema:
                {{
                "events": [
                    "title": "string",
                    "start": "string",      // ISO-8601 date. Include time only if explicitly present or clearly implied by shorthand.
                    "end": "string|null",
                    "all_day": true|false,
                    "notes": "string|null",
                    "confidence": 0.0
                ]
                }}

                Core Rules:
                - The date MUST be {iso_date}.
                - If the OCR text contains no meaningful title, set "title" to "".
                - If the OCR text contains no time, do NOT create, guess, or infer a time.
                - If the OCR text is empty or meaningless, return:
                    "title": "",
                    "notes": "",
                    "all_day": true,
                    "start": "{iso_date}",
                    "end": null,
                    "confidence": 0.0

                Event Grouping Rules:
                - A single planner cell may contain ONE event or MULTIPLE events.
                - Determine grouping based on MEANING, not line count.
                - If multiple lines clearly refer to the same event, merge them into ONE event.
                Example: "14\nValentine's\nbey]" → one event titled "Valentine's".
                - If the lines contain clearly separate, unrelated event descriptions, output multiple events.
                Example: "Dentist 3pm\nDinner with John" → two events.

                Noise and Redundant Text:
                - Ignore numbers that simply repeat the cell date (e.g., "14" inside a cell for the 14th).
                - Ignore stray characters, symbols, or OCR noise (e.g., "bey]", "[]", "|", "*").

                Allowed Inference (Correction Only):
                - You may correct OCR misspellings ONLY when the intended word is obvious.
                Examples:
                    Vicor → Victor
                    Vctor → Victor
                    Victer → Victor
                    Metting → Meeting
                    Brithday → Birthday

                - You may normalize common shorthand patterns when the meaning is unambiguous:
                    "치과/5" → "치과 5시"
                    "Dentist 3" → "Dentist 3pm"
                    "Call-7" → "Call 7pm"

                Forbidden Inference (Never Allowed):
                - Do NOT invent or guess titles such as "Meeting", "Lunch", "Call", etc.
                - Do NOT create times when none exist.
                - Do NOT add notes or details not present in the OCR text.
                - Do NOT fabricate any content.

                Timezone context: {tz}

                OCR text:
                \"\"\"{text}\"\"\"
                """.strip()

    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=120,
    )
    r.raise_for_status()
    raw = r.json()["response"].strip()
    print(raw)
    return json.loads(extract_json(raw))

def extract_json(raw):
    # 1) Remove code fences if present
    raw = raw.replace("```json", "").replace("```", "").strip()

    # 2) Extract JSON substring
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("JSON not found in model output")
    return match.group(0)
