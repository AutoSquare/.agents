# Viewer Integration

Embedded CAD viewers are a separate subsystem from DXF generation. **Fix viewer bugs in the viewer before changing exported geometry** when external CAD or an independent render shows correct output.

## Entity Coverage

Minimum entities for engineering drawings:

- `LINE`
- `LWPOLYLINE` / polyline with width
- `CIRCLE` / `ARC`
- `TEXT` / `MTEXT`
- `DIMENSION`
- `SOLID`
- `INSERT` / block references when the generator or CAD library emits blocks

When an entity is not supported, make the viewer fail visibly or log a warning. Silent omission makes users diagnose layout incorrectly.

## Bounds

Preview zoom and fit depend on bounds. Include:

- Text extents or conservative text boxes.
- Polyline half-width expansion.
- Block reference child entity bounds.
- Solid/fill corners.
- Dimension blocks when dimensions are emitted as anonymous blocks.

Production lesson: a viewer that ignored polyline width made structural lines appear too thin; bounds that ignored half-width could crop thick polylines.

```python
def polyline_bounds_with_width(
    vertices: list[tuple[float, float]],
    max_width_mm: float,
) -> tuple[float, float, float, float]:
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    pad = max_width_mm * 0.5
    return min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
```

## Polyline Width Rendering

When the DXF uses constant or vertex width on polylines, map model width to screen stroke thickness instead of relying on a generic lineweight scale.

```python
def render_polyline_stroke(max_width_mm: float, zoom: float, lineweight_fallback: float) -> float:
    if max_width_mm > 1e-6:
        return max(1.0, max_width_mm * zoom)
    return max(1.0, lineweight_fallback * zoom * 0.01)
```

## Text

DXF text height is not the same as UI font size. Calibrate:

- Font family/fallback for the target language.
- Cap-height or equivalent metrics where available.
- MTEXT line spacing and wrapping.
- Paper-space scale and viewer zoom.

```python
def ui_font_size_from_dxf_height(
    char_height_mm: float,
    scale_y: float,
    zoom: float,
    cap_height_fraction: float = 0.715,
) -> float:
    target_cap_px = char_height_mm * abs(scale_y) * zoom
    return max(target_cap_px / max(cap_height_fraction, 1e-6), 0.1)
```

Compare viewer output against AutoCAD/ODA or a second independent renderer before changing generator geometry.

## Verification

Use a three-surface check:

1. DXF smoke statistics: entity count, layers, bbox.
2. Independent image render: PNG from `ezdxf + matplotlib` or equivalent.
3. Embedded viewer: host app rendering and interaction.

If surface 1 and 2 are correct but surface 3 is wrong, the issue is likely viewer rendering. If all surfaces are wrong, inspect generator/layout.
