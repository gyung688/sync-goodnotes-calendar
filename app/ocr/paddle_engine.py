from __future__ import annotations
from paddleocr import PaddleOCR
from .base import OcrEngine

class PaddleOcrEngine(OcrEngine):
    def __init__(self, lang: str = "en"):
        # lang: "en", "korean", "ch"
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)

    def recognize(self, image_path: str) -> str:
        result = self.ocr.ocr(image_path)
        lines = []
        for page in result:
            for item in page:
                text = item[1][0]
                if text:
                    lines.append(text)
        return "\n".join(lines).strip()
