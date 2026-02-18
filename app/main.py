import argparse
import os

from app.pdf.detector import find_monthly_calendar_pages
from pdf.render import render_pages
from pdf.crop import crop_month_grid_42cells

def cmd_detect(args):
    pages = find_monthly_calendar_pages(args.pdf)
    print("Monthly calendar pages (0-based):", pages)
    print("Monthly calendar pages (1-based):", [p+1 for p in pages])

def cmd_render(args):
    pages = find_monthly_calendar_pages(args.pdf)
    if args.limit:
        pages = pages[: args.limit]
    out_paths = render_pages(args.pdf, pages, args.out, dpi=args.dpi)
    print("Rendered:")
    for p in out_paths:
        print(" -", p)

def cmd_crop(args):
    # render → crop first page (or all)
    pages = find_monthly_calendar_pages(args.pdf)
    if not pages:
        raise SystemExit("No monthly calendar pages found.")
    if args.limit:
        pages = pages[: args.limit]

    page_pngs = render_pages(args.pdf, pages, args.out_pages, dpi=args.dpi)

    for png in page_pngs:
        base = os.path.splitext(os.path.basename(png))[0]
        out_dir = os.path.join(args.out_cells, base)
        paths = crop_month_grid_42cells(png, out_dir)
        print(f"Cropped {len(paths)} cells -> {out_dir}")

def build_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("detect")
    d.add_argument("--pdf", required=True)
    d.set_defaults(func=cmd_detect)

    r = sub.add_parser("render")
    r.add_argument("--pdf", required=True)
    r.add_argument("--out", default="out/pages")
    r.add_argument("--dpi", type=int, default=200)
    r.add_argument("--limit", type=int, default=0)
    r.set_defaults(func=cmd_render)

    c = sub.add_parser("crop")
    c.add_argument("--pdf", required=True)
    c.add_argument("--dpi", type=int, default=200)
    c.add_argument("--out-pages", default="out/pages")
    c.add_argument("--out-cells", default="out/cells")
    c.add_argument("--limit", type=int, default=1)  # 처음엔 1페이지만
    c.set_defaults(func=cmd_crop)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
