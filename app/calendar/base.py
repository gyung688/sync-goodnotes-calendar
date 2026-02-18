from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class CalendarProvider(ABC):
    @abstractmethod
    def upsert_event(self, calendar_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
        ...

    @abstractmethod
    def list_events(self, calendar_id: str, time_min: str, time_max: str) -> Dict[str, Any]:
        ...