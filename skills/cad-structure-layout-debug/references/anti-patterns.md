# CAD Anti-Patterns

## Rejected Layout Patterns

These patterns were tried in production and rejected. Use the portable descriptions below; do not reintroduce them under new names.

### Shifting downstream anchor columns

**Symptom:** moving a fixed downstream column right to give an upstream middle view more room; right-side details and schedule tables then overlap.

**Do instead:** keep the downstream anchor fixed; move the middle view only within its slot (see `layout-engine.md` — Slot Placement with Baseline Floor).

### Paper-bbox over-left-shift

**Symptom:** when the middle view paper bbox slightly intrudes on the downstream column, nudge the middle view far left; large empty gap remains beside the downstream column.

**Do instead:** accept minor paper-bbox overlap if geometry clearance is satisfied; prefer slot centering with baseline floor over aggressive left correction.

### Planned geometry center for stacked bands

**Symptom:** vertically stacked detail views overlap or captions collide because placement used planned geometry height and ignored drawn annotation extent.

**Do instead:** measure actual union `paper_bbox` per band, then top-align chain and distribute slack (`layout-engine.md` — Top-Align Chain Reflow).

## Layout

- Moving downstream columns to hide an upstream collision. Fix the source bbox, anchor, or slot rule instead.
- Centering raw geometry while ignoring captions and dimensions.
- Using planned geometry height for stacked views after annotations are drawn.
- Letting unrelated tables or secondary panels affect the main view scale.
- Applying a global translate to outside-frame tables, notes, or title blocks.

## Verification

- Treating "DXF exists" or "file is non-empty" as success.
- Trusting an embedded preview without checking an external CAD viewer or independent render.
- Changing exported DXF geometry before fixing preview renderer defects.
- Keeping temporary debug labels/log files in delivered code.
- Re-running against stale host binaries after editing the generator.

## Template Quality

- Shipping business-specific names and formulas in a supposedly generic CAD scaffold.
- Hard-coding local drives, user names, private folders, or one-off temp paths.
- Combining domain data loading, layout solving, and DXF entity emission in one large function for new code.
- Rewriting CAD library primitives manually when `ezdxf`, ODA, AutoCAD, or a proven viewer API already provides them.

## Debugging

Good temporary instrumentation:

- bbox values
- chosen scale
- anchor positions
- translate vectors
- entity/layer counts

Remove it or gate it behind explicit debug options before delivery.
