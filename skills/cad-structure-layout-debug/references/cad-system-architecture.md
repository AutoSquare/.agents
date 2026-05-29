# CAD System Architecture

Use this architecture for new CAD drawing components. It is distilled from a production engineering drawing generator, but names and responsibilities are generic.

## Components

| Component | Responsibility |
|---|---|
| Drawing config | Page size, orientation, margins, units, base text height, scale mode, feature toggles. |
| Layer registry | Creates stable layers with colors/linetypes before drawing entities. |
| Domain adapter | Converts project data into view-ready DTOs. Keep it outside layout/export code. |
| View builder | Draws one view or table and returns bbox metadata. |
| Layout solver | Chooses scales, columns/rows, anchors, and translate vectors from bboxes. |
| Exporter | Writes DXF/DWG and handles optional external conversion. |
| Preview adapter | Renders the exported geometry in an app viewer without changing output geometry. |
| Verification harness | Runs smoke checks, PNG render, and focused layout tests. |

## Recommended File Shape

For a Python/ezdxf component:

```text
cad_component/
  drawing_model.py      # Page, BBox, ViewResult, DrawingConfig
  layers.py             # ensure_layers()
  views.py              # bbox-returning view builders
  layout.py             # scale solving and placement
  export_dxf.py         # DXF document creation and save
  generate_example.py   # runnable sample
  tests/                # layout unit tests and smoke checks
```

For a host app:

- Launch the generator through a parameterized CLI or a documented workspace contract.
- Pass input/output paths explicitly.
- Treat cached/prebuilt Python files and host binaries as separate deployment artifacts.
- Rebuild or refresh the host after generator or preview changes.

## BBox Contract

Every drawing function should return:

- `geometry_bbox`: physical geometry only.
- `paper_bbox`: geometry plus captions, dimensions, leaders, labels, and annotation clearance.
- `anchors`: optional named points such as `top`, `bottom`, `right_edge`, `schedule_origin`.

Layout decisions should use `paper_bbox` unless the rule explicitly concerns raw geometry. This prevents captions, dimensions, and labels from overlapping even when geometry itself fits.

## Export Contract

Minimum exporter behavior:

- Use modelspace units consistently, normally paper millimeters for sheet layout.
- Create required layers before drawing.
- Save to caller-provided output path.
- Report structured status to the host: success/failure, output path, warnings.
- Never rely on current working directory unless documented.

## Provenance Rule

When adapting lessons from a production engineering drawing generator, preserve the pattern but remove project-specific nouns, table names, path conventions, and business formulas. A template should teach how to create CAD components, not recreate the original product.
