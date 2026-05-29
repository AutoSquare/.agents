# -*- coding: utf-8 -*-
"""Structural smoke checks for DXF engineering drawing output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import ezdxf
except ImportError as exc:
    raise SystemExit("Missing dependency: install ezdxf to run this checker.") from exc


def inspect_dxf(path: Path, *, min_entities: int, require_layers: list[str]) -> dict:
    if not path.is_file():
        raise SystemExit(f"DXF not found: {path}")
    if path.stat().st_size <= 0:
        raise SystemExit(f"DXF is empty: {path}")

    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    entities = list(msp)
    if len(entities) < min_entities:
        raise SystemExit(f"Too few modelspace entities: {len(entities)} < {min_entities}")

    layer_names = {layer.dxf.name for layer in doc.layers}
    missing = [name for name in require_layers if name not in layer_names]
    if missing:
        raise SystemExit(f"Missing required layers: {', '.join(missing)}")

    bbox = None
    try:
        from ezdxf import bbox as ezbbox

        extents = ezbbox.extents(entities)
        if extents.has_data:
            bbox = [
                round(float(extents.extmin.x), 3),
                round(float(extents.extmax.x), 3),
                round(float(extents.extmin.y), 3),
                round(float(extents.extmax.y), 3),
            ]
    except Exception:
        bbox = None

    entity_types: dict[str, int] = {}
    for entity in entities:
        entity_types[entity.dxftype()] = entity_types.get(entity.dxftype(), 0) + 1

    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "entities": len(entities),
        "layers": sorted(layer_names),
        "entity_types": entity_types,
        "bbox": bbox,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dxf", required=True, help="Path to DXF file.")
    parser.add_argument("--min-entities", type=int, default=10)
    parser.add_argument("--require-layer", action="append", default=[], help="Required layer name; repeatable.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    info = inspect_dxf(Path(args.dxf), min_entities=args.min_entities, require_layers=args.require_layer)
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            f"OK dxf={info['path']} bytes={info['bytes']} entities={info['entities']} "
            f"layers={len(info['layers'])} bbox={info['bbox']} types={info['entity_types']}"
        )


if __name__ == "__main__":
    main()
