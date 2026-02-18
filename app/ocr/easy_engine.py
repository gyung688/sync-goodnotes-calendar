from __future__ import annotations
import easyocr
from .base import OcrEngine

class EasyOcrEngine(OcrEngine):
    def __init__(self, languages=("en", "ko")):
        # self.reader = easyocr.Reader(list(languages), gpu=False)
        self.reader = easyocr.Reader(list(languages), gpu=False, detector='openvino')

    def recognize(self, image_path: str) -> str:
        results = self.reader.readtext(image_path, detail=0, paragraph=False)
        # results: list[str]
        lines = [t.strip() for t in results if t and t.strip()]
        return "\n".join(lines)
