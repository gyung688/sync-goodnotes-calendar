from __future__ import annotations
import os
import hashlib
from typing import Dict, Any, Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def stable_ical_uid(source: str) -> str:
    # 결정적 UID: 같은 source면 항상 같은 iCalUID가 됨
    h = hashlib.sha1(source.encode("utf-8")).hexdigest()
    return f"{h}@goodnotes.local"

class GoogleCalendarProvider:
    def __init__(self, credentials_path: str, token_path: str):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self._service = None

    def _creds(self) -> Credentials:
        creds: Optional[Credentials] = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())

        return creds

    def service(self):
        if self._service is None:
            self._service = build("calendar", "v3", credentials=self._creds())
        return self._service

    def upsert_event(self, calendar_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        event must include:
        - summary
        - start/end (date or dateTime)
        - iCalUID (we will set if missing)
        """
        svc = self.service()

        if "iCalUID" not in event:
            raise ValueError("event missing iCalUID")

        found = svc.events().list(calendarId=calendar_id, iCalUID=event["iCalUID"]).execute()
        items = found.get("items", [])

        if items:
            event_id = items[0]["id"]
            return svc.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        return svc.events().insert(calendarId=calendar_id, body=event).execute()

    def list_events(self, calendar_id: str, time_min: str, time_max: str) -> Dict[str, Any]:
        svc = self.service()
        return svc.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        ).execute()