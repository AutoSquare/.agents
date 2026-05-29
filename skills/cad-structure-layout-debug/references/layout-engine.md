# Layout Engine

## Principles

- Separate scale choice, view placement, and final translate.
- Use actual drawn bboxes for downstream placement whenever annotations can change size.
- Keep independent budgets independent. A table or secondary panel should not shrink the main view unless the drawing contract couples them.
- Use named anchors and bboxes instead of magic offsets.
- **Fix downstream anchors when the contract says they are fixed.** Do not shift a later column or band to hide an upstream overlap.

## Geometry BBox vs Paper BBox

Raw geometry is not enough for layout. Dimensions, captions, leaders, text, hatch labels, and table titles extend beyond geometry.

Use this model:

```python
ViewResult(
    entities=[...],
    geometry_bbox=BBox(...),
    paper_bbox=BBox(...),
    anchors={"top": (x, y), "right": (x, y)}
)
```

Place adjacent views by `paper_bbox`. Use `geometry_bbox` only for rules such as centering a shape within its own view.

## Scale Selection

Recommended flow:

1. Compute available width/height for each **independent band**.
2. Compute required model extents per view group.
3. Pick the smallest denominator that fits and remains readable.
4. Avoid fallback-to-max-scale unless the geometry truly cannot fit.
5. Unit-test scale selection with exaggerated secondary content to ensure budgets do not leak.

**Independent scale budget:** a secondary details/table column was accidentally included in the main elevation scale solver and forced an unreadable max-scale drawing. The fix was to choose the main band scale only from the main band height budget.

```python
def pick_main_band_scale(page_h: float, model_length: float, scale_levels: tuple[int, ...]) -> int:
    """Main view band scale from height budget only — ignore right-side panel width."""
    top_pad = 10.0
    bottom_reserve = 18.0
    h_avail = page_h * 0.98 - top_pad - bottom_reserve * 0.35
    for n in scale_levels:
        band_h = model_length / float(n) + 18.0
        if band_h <= h_avail:
            return int(n)
    return int(scale_levels[-1])
```

## Fixed Downstream Anchor

When a downstream view column has a **fixed origin** in the layout contract, compute it before placing the middle view. Never increase that origin to resolve overlap with an upstream view.

```python
def compute_middle_view_and_fixed_anchor(
    left_band_right: float,
    middle_draw_w: float,
    band_gap: float,
) -> tuple[float, float]:
    """Middle view moves only inside its slot; downstream anchor stays fixed."""
    downstream_anchor = (
        float(left_band_right) + float(band_gap) + float(middle_draw_w) + float(band_gap)
    )
    baseline_x = float(left_band_right) + float(band_gap)
    return baseline_x, downstream_anchor  # caller adjusts middle_x within [baseline, max_x]
```

## Slot Placement with Baseline Floor

Move a middle view **only within its allowed slot**. Include annotation extent from the left neighbor when computing the slot left bound. Prefer center-in-slot with a baseline floor: move right only when the ideal center is right of baseline; never shift the fixed downstream anchor.

```python
def place_middle_view_in_slot(
    left_paper_right: float,
    left_label_extent: float,
    middle_draw_w: float,
    band_gap: float,
    downstream_anchor: float,
    geom_clear: float,
) -> float:
    baseline_x = float(left_band_right) + float(band_gap)
    max_x = float(downstream_anchor) - float(middle_draw_w) - float(geom_clear)
    effective_left = max(float(left_paper_right), float(left_label_extent))
    ideal_x = (effective_left + max_x) * 0.5
    if ideal_x > baseline_x + 1e-6:
        return min(ideal_x, max_x)
    return baseline_x
```

Rejected companion fix: shifting `downstream_anchor` right when `baseline_x > max_x`. That breaks the right-side panel.

## Placement

Use a deterministic sequence:

1. Draw or estimate the first band and collect `paper_bbox`.
2. Compute the next band origin from the previous band's right edge plus a named gap.
3. Draw the next band and collect its bbox.
4. Reflow stacked subviews using actual union bboxes, not planned geometry heights.
5. Apply any global centering translate only to entities that belong to the main band.
6. Draw outside-frame tables or fixed notes after the main translate, or exclude them from that translate.

## Stacked Views — Top-Align Chain Reflow

For vertical stacks:

- Draw each band at a temporary or nominal position.
- Measure each actual `paper_bbox` (union after draw).
- Compute total stack height.
- Distribute vertical slack across top, bottom, and inter-band gaps.
- Translate each band by its own delta.

Do **not** place stacked bands by planned geometry center when captions and dimensions extend the paper bbox.

```python
def reflow_stacked_bands_top_align(
    band_bboxes: list[tuple[float, float, float, float]],
    top_y: float,
    floor_y: float,
) -> list[float]:
    """Top-align chain; distribute slack evenly across n+1 gaps."""
    heights = [bb[3] - bb[2] for bb in band_bboxes]
    total_h = sum(heights)
    available = max(float(top_y) - float(floor_y), total_h)
    gap = max(0.0, (available - total_h) / float(len(band_bboxes) + 1))
    deltas: list[float] = []
    y_top = float(top_y) - gap
    for bb in band_bboxes:
        deltas.append(y_top - bb[3])  # dy to apply to band entities
        y_top = bb[2] + deltas[-1] - gap
    return deltas
```

## Table Anchors

For schedules and tables, solve both horizontal and vertical feasibility:

- `inside_frame`: table width fits with right/left alignment and vertical stack clears notes/title block.
- `outside_frame`: explicit policy only; **outside tables must be excluded from main drawing translate**.
- `right_aligned`: clamp the table right edge to the inner frame when inside.
- `notes_floor`: reserve bottom text/title block area before accepting inside placement.

Do not use width-only tests such as `column_width >= table_width` if the table may be right-aligned across adjacent free space.

```python
def resolve_schedule_anchor(
    inner_left: float,
    inner_right: float,
    table_w: float,
    pad: float,
    outside_x: float,
) -> tuple[float, bool]:
    """Returns (anchor_x, outside_frame). Outside tables skip main-band translate."""
    right_aligned_x = inner_right - table_w - pad
    fits = table_w > 0 and right_aligned_x >= inner_left + pad
    if not fits:
        return outside_x, True
    return max(inner_left + pad, right_aligned_x), False
```

## Testing Rules

Write unit tests for:

- Scale does not change when unrelated secondary content grows.
- Adjacent paper bboxes do not overlap (or overlap is within documented tolerance).
- Middle view stays at or right of baseline when slot allows; downstream anchor unchanged.
- Stacked view gaps are non-negative and reasonably even after actual-bbox reflow.
- Tables stay inside when feasible and outside only by explicit policy.
- Global translate does not move fixed/outside elements incorrectly.
