# -*- coding: utf-8 -*-
"""Scaffold a small, project-neutral CAD drawing component."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FILES: dict[str, str] = {
    "drawing_model.py": '''# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field

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


@dataclass(frozen=True)
class DrawingConfig:
    page: Page = field(default_factory=Page)
    base_text_height: float = 3.0


@dataclass(frozen=True)
class ViewResult:
    geometry_bbox: BBox
    paper_bbox: BBox
    anchors: dict[str, tuple[float, float]] = field(default_factory=dict)


def union_bbox(*boxes: BBox) -> BBox:
    return (
        min(b[0] for b in boxes),
        max(b[1] for b in boxes),
        min(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )
''',
    "layers.py": '''# -*- coding: utf-8 -*-
from __future__ import annotations

import ezdxf


LAYERS = {
    "FRAME": 1,
    "VIEW": 2,
    "DIM": 4,
    "TEXT": 5,
    "TABLE": 3,
    "NOTES": 6,
}


def ensure_layers(doc: ezdxf.EzDxf) -> None:
    for name, color in LAYERS.items():
        if name not in doc.layers:
            doc.layers.add(name, color=color)
''',
    "views.py": '''# -*- coding: utf-8 -*-
from __future__ import annotations

import ezdxf

from drawing_model import BBox, ViewResult, union_bbox


def draw_caption(msp: ezdxf.layouts.Modelspace, text: str, x: float, y: float, width: float) -> BBox:
    msp.add_text(text, height=3.5, dxfattribs={"layer": "TEXT"}).set_placement((x + width * 0.25, y - 8.0))
    msp.add_line((x + width * 0.2, y - 9.5), (x + width * 0.8, y - 9.5), dxfattribs={"layer": "TEXT"})
    return (x, x + width, y - 11.0, y)


def draw_rect_view(msp: ezdxf.layouts.Modelspace, x: float, y: float, width: float, height: float, caption: str) -> ViewResult:
    msp.add_lwpolyline([(x, y), (x + width, y), (x + width, y + height), (x, y + height), (x, y)], dxfattribs={"layer": "VIEW"})
    msp.add_line((x, y), (x + width, y + height), dxfattribs={"layer": "DIM"})
    msp.add_line((x, y + height), (x + width, y), dxfattribs={"layer": "DIM"})
    geometry = (x, x + width, y, y + height)
    paper = union_bbox(geometry, draw_caption(msp, caption, x, y, width))
    return ViewResult(geometry_bbox=geometry, paper_bbox=paper, anchors={"top": (x + width / 2.0, y + height)})


def draw_schedule(msp: ezdxf.layouts.Modelspace, x: float, y_top: float) -> ViewResult:
    rows = [("Item", "Qty"), ("A", "4"), ("B", "8")]
    col_w = [36.0, 28.0]
    row_h = 8.0
    total_w = sum(col_w)
    total_h = row_h * len(rows)
    y_bottom = y_top - total_h
    msp.add_lwpolyline([(x, y_bottom), (x + total_w, y_bottom), (x + total_w, y_top), (x, y_top), (x, y_bottom)], dxfattribs={"layer": "TABLE"})
    msp.add_line((x + col_w[0], y_bottom), (x + col_w[0], y_top), dxfattribs={"layer": "TABLE"})
    for i, row in enumerate(rows):
        yy = y_top - i * row_h
        if i > 0:
            msp.add_line((x, yy), (x + total_w, yy), dxfattribs={"layer": "TABLE"})
        msp.add_text(row[0], height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((x + 2.0, yy - row_h + 2.2))
        msp.add_text(row[1], height=2.5, dxfattribs={"layer": "TEXT"}).set_placement((x + col_w[0] + 2.0, yy - row_h + 2.2))
    bbox = (x, x + total_w, y_bottom, y_top)
    return ViewResult(geometry_bbox=bbox, paper_bbox=bbox, anchors={"right": (x + total_w, y_top)})
''',
    "layout.py": '''# -*- coding: utf-8 -*-
from __future__ import annotations

from drawing_model import Page


def view_origins(page: Page) -> dict[str, tuple[float, float]]:
    return {
        "main": (page.inner_left + 20.0, page.inner_bottom + 72.0),
        "detail": (page.inner_left + 150.0, page.inner_bottom + 165.0),
        "schedule": (page.inner_right - 70.0, page.inner_top - 120.0),
    }
''',
    "export_dxf.py": '''# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import ezdxf

from drawing_model import DrawingConfig
from layers import ensure_layers
from layout import view_origins
from views import draw_rect_view, draw_schedule


def draw_frame(msp: ezdxf.layouts.Modelspace, cfg: DrawingConfig) -> None:
    page = cfg.page
    msp.add_lwpolyline([(0, 0), (page.width, 0), (page.width, page.height), (0, page.height), (0, 0)], dxfattribs={"layer": "FRAME"})
    msp.add_lwpolyline(
        [(page.inner_left, page.inner_bottom), (page.inner_right, page.inner_bottom), (page.inner_right, page.inner_top), (page.inner_left, page.inner_top), (page.inner_left, page.inner_bottom)],
        dxfattribs={"layer": "FRAME"},
    )
    msp.add_text("CAD Component Example", height=4.0, dxfattribs={"layer": "TEXT"}).set_placement((page.inner_right - 160.0, page.inner_bottom + 8.0))


def generate(out: Path, cfg: DrawingConfig | None = None) -> None:
    cfg = cfg or DrawingConfig()
    doc = ezdxf.new("R2010")
    ensure_layers(doc)
    msp = doc.modelspace()
    draw_frame(msp, cfg)
    origins = view_origins(cfg.page)
    draw_rect_view(msp, *origins["main"], 70.0, 150.0, "Main View")
    draw_rect_view(msp, *origins["detail"], 58.0, 58.0, "Detail")
    draw_schedule(msp, *origins["schedule"])
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(out)
''',
    "generate_example.py": '''# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
from pathlib import Path

from export_dxf import generate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    generate(Path(args.out))
    print(f"OK generated={args.out}")


if __name__ == "__main__":
    main()
''',
}


def normalize_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", name.strip()).strip("-_")
    return cleaned or "cad_component"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Target directory for the component.")
    parser.add_argument("--name", default="cad_component", help="Component name used for the top-level folder when --out is a parent directory.")
    parser.add_argument("--force", action="store_true", help="Allow writing into an existing empty directory.")
    args = parser.parse_args()

    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()) and not args.force:
        raise SystemExit(f"Target directory exists and is not empty: {out}")
    out.mkdir(parents=True, exist_ok=True)

    for relative, content in FILES.items():
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    readme = (
        f"# {normalize_name(args.name)}\n\n"
        "Minimal CAD drawing component scaffold.\n\n"
        "Run:\n\n"
        "```powershell\n"
        "py -3.10 generate_example.py --out out/example.dxf\n"
        "```\n"
    )
    (out / "README.md").write_text(readme, encoding="utf-8")
    print(f"OK scaffold={out}")


if __name__ == "__main__":
    main()
