from __future__ import annotations
from datetime import datetime, date, timedelta
from dateutil.parser import isoparse

def google_event_from_extracted(
    extracted: dict,
    tz: str,
    ical_uid: str,
) -> dict:
    """
    extracted: {"title","start","end","all_day","notes",...}
    """
    title = (extracted.get("title") or "").strip()
    if not title:
        raise ValueError("empty title")

    all_day = bool(extracted.get("all_day"))
    start_raw = extracted["start"]
    end_raw = extracted.get("end")

    body = {
        "summary": title,
        "description": (extracted.get("notes") or "").strip() or None,
        "iCalUID": ical_uid,
    }

    if all_day:
        # start_raw is YYYY-MM-DD
        d = date.fromisoformat(start_raw[:10])
        body["start"] = {"date": d.isoformat()}
        body["end"] = {"date": (d + timedelta(days=1)).isoformat()}
    else:
        start_dt = isoparse(start_raw)
        if end_raw:
            end_dt = isoparse(end_raw)
        else:
            # end가 없으면 1시간 기본
            end_dt = start_dt + timedelta(hours=1)

        body["start"] = {"dateTime": start_dt.isoformat(), "timeZone": tz}
        body["end"] = {"dateTime": end_dt.isoformat(), "timeZone": tz}

    # None 제거(구글은 description None도 보통 OK지만 깔끔하게)
    return {k: v for k, v in body.items() if v is not None}