#!/usr/bin/env python3
"""Render a PDF with Poppler and optionally build a contact sheet."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


def find_pdftoppm(explicit: str | None) -> str:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.exists():
            return str(path)
        raise SystemExit(f"pdftoppm not found: {path}")
    found = shutil.which("pdftoppm")
    if found:
        return found
    raise SystemExit("pdftoppm is required. Install Poppler or pass --pdftoppm.")


def page_number(path: Path) -> int:
    match = re.search(r"(\d+)$", path.stem)
    return int(match.group(1)) if match else 0


def make_contact_sheet(pages: list[Path], output: Path) -> bool:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Pillow unavailable; PNG rendering succeeded without a contact sheet.")
        return False

    thumb_w, thumb_h, label_h, columns = 248, 351, 24, 4
    rows = (len(pages) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, page in enumerate(pages):
        with Image.open(page) as opened:
            image = opened.convert("RGB")
            image.thumbnail((thumb_w - 8, thumb_h - 8))
            x = (index % columns) * thumb_w + (thumb_w - image.width) // 2
            y = (index // columns) * (thumb_h + label_h)
            sheet.paste(image, (x, y))
            draw.text((x + 4, y + thumb_h), f"{index + 1:02d}", fill="#24313B")
    sheet.save(output, quality=90)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("render_dir", type=Path)
    parser.add_argument("--dpi", type=int, default=120)
    parser.add_argument("--pdftoppm")
    args = parser.parse_args()

    pdf = args.pdf.expanduser().resolve()
    render_dir = args.render_dir.expanduser().resolve()
    if render_dir.exists() and any(render_dir.iterdir()):
        raise SystemExit(f"Render directory is not empty: {render_dir}")
    render_dir.mkdir(parents=True, exist_ok=True)

    executable = find_pdftoppm(args.pdftoppm)
    prefix = render_dir / "page"
    subprocess.run(
        [executable, "-png", "-r", str(args.dpi), str(pdf), str(prefix)],
        check=True,
    )
    pages = sorted(render_dir.glob("page-*.png"), key=page_number)
    if not pages:
        raise SystemExit("Poppler returned no rendered pages.")
    contact = render_dir / "contact-sheet.jpg"
    made = make_contact_sheet(pages, contact)
    print(f"pages={len(pages)}")
    if made:
        print(f"contact_sheet={contact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
