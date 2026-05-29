# -*- coding: utf-8 -*-
"""Render a DXF modelspace to a PNG preview for minimum visual verification."""

from __future__ import annotations

import argparse
from pathlib import Path


def render(dxf: Path, png: Path, *, dpi: int) -> None:
    try:
        import ezdxf
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import Frontend, RenderContext
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        from PIL import Image
    except ImportError as exc:
        raise SystemExit(f"Missing dependency for PNG render: {exc}") from exc

    if not dxf.is_file():
        raise SystemExit(f"DXF not found: {dxf}")

    doc = ezdxf.readfile(dxf)
    fig = plt.figure(figsize=(16, 10), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    ax.axis("off")
    Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(doc.modelspace(), finalize=True)
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=dpi)
    plt.close(fig)

    with Image.open(png) as image:
        image.verify()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dxf", required=True, help="Input DXF path.")
    parser.add_argument("--png", required=True, help="Output PNG path.")
    parser.add_argument("--dpi", type=int, default=150)
    args = parser.parse_args()
    render(Path(args.dxf), Path(args.png), dpi=args.dpi)
    print(f"OK rendered={args.png}")


if __name__ == "__main__":
    main()
