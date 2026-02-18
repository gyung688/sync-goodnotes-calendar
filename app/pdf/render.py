import os
import fitz  # PyMuPDF

def render_pages(pdf_path: str, page_indexes: list[int], out_dir: str, dpi: int = 200) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)

    zoom = dpi / 72  # 72 DPI is the default resolution of PDF points
    mat = fitz.Matrix(zoom, zoom)

    out_paths: list[str] = []
    for idx in page_indexes:
        page = doc.load_page(idx)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out_path = os.path.join(out_dir, f"page_{idx+1:03d}.png")  # file name with 1-based page number, zero-padded
        pix.save(out_path)
        out_paths.append(out_path)

    return out_paths
