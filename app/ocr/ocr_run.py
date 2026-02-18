import os
import json
# from ocr.paddle_engine import PaddleOcrEngine
from ocr.easy_engine import EasyOcrEngine

def ocr_cells(cells_dir: str, out_json: str, lang="korean"):
    engine = EasyOcrEngine(languages=("en", "ko"))
    data = {}
    for root, _, files in os.walk(cells_dir):
        for f in sorted(files):
            if not f.lower().endswith(".png"):
                continue
            path = os.path.join(root, f)
            text = engine.recognize(path)
            data[path.replace("\\", "/")] = text

    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # example: out/cells/page_033/
    ocr_cells("out/cells/page_033", "out/ocr/page_033.json", lang="korean")
    print("Saved OCR:", "out/ocr/page_033.json")
