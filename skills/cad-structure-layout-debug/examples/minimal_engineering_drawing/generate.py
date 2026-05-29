# -*- coding: utf-8 -*-
"""Generate a minimal multi-view engineering drawing with ezdxf."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import ezdxf
except ImportError as exc:
    raise SystemExit("Missing dependency: install ezdxf to run this example.") from exc


BBox = tuple[float, float, float, float]


@dataclass(frozen=True)
class Page:
    width: float = 420.0
    height: float = 297.0
    margin_left: float = 20.0
    margin_right: float = 12.0
    margin_top: float = 12.0
    margin_bottom: float = 12.0

    @property
    def inner_left(self) -> float:
        return self.margin_left

    @property
    def inner_right(self) -> float:
        return self.width - self.margin_right

    @property
    def inner_bottom(self) -> float:
        return self.margin_bottom

    @property
    def inner_top(self) -> float:
        return self.height - self.margin_top


def union_bbox(items: Iterable[BBox]) -> BBox:
    boxes = list(items)
    return (
        min(b[0] for b in boxes),
        max(b[1] for b in boxes),
        min(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )


def ensure_layers(doc: ezdxf.EzDxf) -> None:
    for name, color in {
        "FRAME": 1,
        "VIEW": 2,
        "DIM": 4,
        "TEXT": 5,
        "TABLE": 3,
        "NOTES": 6,
    }.items():
        if name not in doc.layers:
            doc.layers.add(name, color=color)


def draw_frame(msp: ezdxf.layouts.Modelspace, page: Page) -> BBox:
    msp.add_lwpolyline(
        [(0, 0), (page.width, 0), (page.width, page.height), (0, page.height), (0, 0)],
        dxfattribs={"layer": "FRAME"},
    )
    msp.add_lwpolyline(
        [
            (page.inner_left, page.inner_bottom),
            (page.inner_right, page.inner_bottom),
            (page.inner_right, page.inner_top),
            (page.inner_left, page.inner_top),
            (page.inner_left, page.inner_bottom),
        ],
        dxfattribs={"layer": "FRAME"},
    )
    title_w = 170.0
    title_h = 28.0
    x0 = page.inner_right - title_w
    y0 = page.inner_bottom
    msp.add_lwpolyline(
        [(x0, y0), (page.inner_right, y0), (page.inner_right, y0 + title_h), (x0, y0 + title_h), (x0, y0)],
        dxfattribs={"layer": "FRAME"},
    )
    for x in (x0 + 80.0, x0 + 120.0):
        msp.add_line((x, y0), (x, y0 + title_h), dxfattribs={"layer": "FRAME"})
    for y in (y0 + 9.0, y0 + 18.0):
        msp.add_line((x0, y), (page.inner_right, y), dxfattribs={"layer": "FRAME"})
    msp.add_text("Example CAD Sheet", height=4.0, dxfattribs={"layer": "TEXT"}).set_placement((x0 + 5.0, y0 + 19.5))
    return (0.0, page.width, 0.0, page.height)


def draw_caption(msp: ezdxf.layouts.Modelspace, text: str, x: float, y: float, width: float) -> BBox:
    msp.add_text(text, height=3.5, dxfattribs={"layer": "TEXT"}).set_placement((x + width * 0.25, y - 8.0))
    msp.add_line((x + width * 0.2, y - 9.5), (x + width * 0.8, y - 9.5), dxfattribs={"layer": "TEXT"})
    return (x, x + width, y - 11.0, y)


def draw_elevation(msp: ezdxf.layouts.Modelspace, x: float, y: float, width: float, height: float) -> BBox:
    msp.add_lwpolyline([(x, y), (x + width, y), (x + width, y + height), (x, y + height), (x, y)], dxfattribs={"layer": "VIEW"})
    for i in range(1, 5):
        xi = x + width * i / 5.0
        msp.add_line((xi, y), (xi, y + height), dxfattribs={"layer": "VIEW"})
    for i in range(1, 8):
        yi = y + height * i / 8.0
        msp.add_line((x, yi), (x + width, yi), dxfattribs={"layer": "DIM"})
    dim_x = x - 8.0
    msp.add_line((dim_x, y), (dim_x, y + height), dxfattribs={"layer": "DIM"})
    msp.add_text("H", height=3.0, dxfattribs={"layer": "TEXT"}).set_placement((dim_x - 2.0, y + height * 0.5))
    geo = (x, x + width, y, y + height)
    cap = draw_caption(msp, "Elevation", x, y, width)
    return union_bbox([geo, cap, (dim_x - 4.0, x + width, y, y + height)])


def draw_detail(msp: ezdxf.layouts.Modelspace, x: float, y: float, size: float) -> BBox:
    msp.add_lwpolyline([(x, y), (x + size, y), (x + size, y + size), (x, y + size), (x, y)], dxfattribs={"layer": "VIEW"})
    msp.add_circle((x + size * 0.5, y + size * 0.5), size * 0.28, dxfattribs={"layer": "VIEW"})
    msp.add_line((x, y), (x + size, y + size), dxfattribs={"layer": "DIM"})
    msp.add_line((x, y + size), (x + size, y), dxfattribs={"layer": "DIM"})
    geo = (x, x + size, y, y + size)
    cap = draw_caption(msp, "Detail", x, y, size)
    return union_bbox([geo, cap])


def draw_schedule(msp: ezdxf.layouts.Modelspace, x: float, y_top: float) -> BBox:
    col_w = [34.0, 34.0, 44.0]
    row_h = 8.0
    rows = [
        ("Item", "Qty", "Remark"),
        ("A", "4", "main"),
        ("B", "8", "stirrup"),
        ("C", "2", "detail"),
    ]
    total_w = sum(col_w)
    total_h = row_h * len(rows)
    y_bottom = y_top - total_h
    msp.add_lwpolyline([(x, y_bottom), (x + total_w, y_bottom), (x + total_w, y_top), (x, y_top), (x, y_bottom)], dxfattribs={"layer": "TABLE"})
    xx = x
    for w in col_w[:-1]:
        xx += w
        msp.add_line((xx, y_bottom), (xx, y_top), dxfattribs={"layer": "TABLE"})
    for i, row in enumerate(rows):
        yy = y_top - row_h * i
        if i > 0:
            msp.add_line((x, yy), (x + total_w, yy), dxfattribs={"layer": "TABLE"})
        cx = x + 2.0
        for value, w in zip(row, col_w):
            msp.add_text(value, height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((cx, yy - row_h + 2.2))
            cx += w
    return (x, x + total_w, y_bottom, y_top)


def draw_notes(msp: ezdxf.layouts.Modelspace, page: Page) -> BBox:
    text = "Notes: verify DXF in an external viewer; do not accept non-empty files without visual checks."
    x = page.inner_left + 2.0
    y = page.inner_bottom + 8.0
    msp.add_mtext(text, dxfattribs={"layer": "NOTES", "char_height": 2.8, "width": 180.0}).set_location((x, y))
    return (x, x + 180.0, y - 5.0, y + 8.0)


def generate(out: Path) -> None:
    page = Page()
    doc = ezdxf.new("R2010")
    ensure_layers(doc)
    msp = doc.modelspace()
    draw_frame(msp, page)
    draw_elevation(msp, page.inner_left + 18.0, 70.0, 48.0, 175.0)
    draw_elevation(msp, page.inner_left + 92.0, 70.0, 48.0, 175.0)
    draw_detail(msp, page.inner_left + 178.0, 165.0, 62.0)
    draw_detail(msp, page.inner_left + 265.0, 180.0, 45.0)
    draw_schedule(msp, page.inner_right - 118.0, 145.0)
    draw_notes(msp, page)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Output DXF path.")
    args = parser.parse_args()
    generate(Path(args.out))
    print(f"OK generated={args.out}")


if __name__ == "__main__":
    main()
