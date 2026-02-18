import os
from PIL import Image

def crop_month_grid_42cells(
    page_png: str,
    out_dir: str,
    grid_box_ratio=(0.055, 0.14, 0.78, 0.94),  # (left, top, right, bottom) in ratios
    rows=6,
    cols=7,
):
    """
    crop the monthly grid area into 7x6=42 cells.
    grid_box_ratio is a 'rough' starting value, once adjusted it can be fixed.
    """
    os.makedirs(out_dir, exist_ok=True)
    img = Image.open(page_png).convert("RGB")
    w, h = img.size

    l, t, r, b = grid_box_ratio
    L, T, R, B = int(w*l), int(h*t), int(w*r), int(h*b)

    grid = img.crop((L, T, R, B))
    gw, gh = grid.size
    cw, ch = gw / cols, gh / rows

    cell_paths = []
    for rr in range(rows):
        for cc in range(cols):
            x1 = int(cc * cw)
            y1 = int(rr * ch)
            x2 = int((cc + 1) * cw)
            y2 = int((rr + 1) * ch)

            cell = grid.crop((x1, y1, x2, y2))
            out_path = os.path.join(out_dir, f"cell_r{rr+1}_c{cc+1}.png")
            cell.save(out_path)
            cell_paths.append(out_path)

    return cell_paths
