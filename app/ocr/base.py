from __future__ import annotations
from abc import ABC, abstractmethod

class OcrEngine(ABC):
    @abstractmethod
    def recognize(self, image_path: str) -> str:
        ...
