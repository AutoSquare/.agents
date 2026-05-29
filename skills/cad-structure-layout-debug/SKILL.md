---
name: cad-structure-layout-debug
description: 从零搭建或调试工程 CAD 出图组件（Python/ezdxf、DXF 排版、布局引擎、明细表锚点、预览与 AutoCAD 一致性、烟测与视觉验收）。用于图纸太小/留白大/视图重叠/比例误跳/表飞出/预览不一致/文件锁/宿主 Rebuild 等问题；或用户 @ 本 Skill、提及工程图排版/CAD 布局调试。
disable-model-invocation: true
---

# CAD Structure Layout Debug

Use this skill to build or repair CAD drawing capability for any project. Do not assume the target project has a specific host app, workspace format, or proprietary generator module.

## Generic Boundary

Do not copy host business drawing code into another project. When creating templates, keep only generic architecture and algorithms: page models, layer registries, bbox contracts, layout solvers, table anchors, exporters, preview adapters, and verification scripts.

## Triage

Classify first, then build or edit:

1. **Generator**: input parsing, drawing model, layers, view builders, dimensions, schedules, DXF/DWG export.
2. **Layout**: geometry bbox vs paper bbox, scale selection, view bands, row/column placement, table anchors, translate order.
3. **Preview**: embedded viewer text height, polyline width, INSERT/SOLID, font fallback, background/contrast, bbox bounds.
4. **Host integration**: CLI/stdin/workspace contract, cache, rebuild, status bar, export path, validation before drawing.
5. **Environment**: missing CAD libraries, file locks, external CAD/ODA availability, stale binaries, path encoding.

Read only what is needed:

- `references/cad-system-architecture.md`: generic CAD component architecture.
- `references/layout-engine.md`: bbox-driven layout, slot rules, scale solving, code patterns.
- `references/viewer-integration.md`: embedded preview and external CAD comparison.
- `references/anti-patterns.md`: rejected fixes and failure modes.
- `references/layout-case-studies.md`: anonymous production lessons.

## Cursor Usage

- This skill is managed by `.agents/scripts/setup-cursor-agents.ps1` through `installManifest.managedSkills`.
- After installation, use it from `%USERPROFILE%\.cursor\skills\cad-structure-layout-debug\` (or `@cad-structure-layout-debug` in chat).
- First classify the issue with **Triage**, then read only the relevant file under `references/`; see `README-cursor.md` for install and verification.
- This skill covers **CAD drawing, DXF layout, preview, and visual verification**. Backend calculation debugging should use a project-specific backend-debug skill if one exists.

## Codex Usage

- This skill is managed by `.agents/scripts/setup-codex-agents.ps1` through `codexInstallManifest.managedSkills`.
- After installation, use it from `$CODEX_HOME/skills/cad-structure-layout-debug/`.
- First classify the issue with **Triage**, then read only the relevant file under `references/`.
- This skill covers **CAD drawing, DXF layout, preview, and visual verification**. Backend calculation debugging should use a project-specific backend-debug skill if one exists.

## From Scratch Workflow

1. Define the drawing contract before writing entities: page, units, margins, layers, views, captions, dimensions, notes, schedules, output files.
2. Create a drawing model separate from DXF API calls. Keep domain data, paper layout, and exporter concerns distinct.
3. Build every view as a function that returns both geometry bbox and paper bbox. Paper bbox must include captions, labels, dimensions, leaders, and other annotations.
4. Select scale from the view band's own budget unless a product rule explicitly couples bands. Do not let unrelated tables or right-side panels shrink the main drawing.
5. Place views in deterministic order using prior bboxes and named anchors, not guessed constants.
6. Anchor tables explicitly: inside frame when width and vertical stack fit; outside only by policy. Outside tables must not participate in the main drawing translate.
7. Save DXF, run smoke checks, render PNG, then inspect in an external CAD viewer when possible.

## Template Workflow

For a new project, start with the scaffold:

```powershell
py -3.10 scripts/scaffold_cad_component.py --out "<target-dir>" --name "<component-name>"
```

Then run the generated example:

```powershell
py -3.10 "<target-dir>/generate_example.py" --out "<target-dir>/out/example.dxf"
py -3.10 scripts/dxf_smoke_check.py --dxf "<target-dir>/out/example.dxf" --min-entities 10
py -3.10 scripts/render_dxf_preview.py --dxf "<target-dir>/out/example.dxf" --png "<target-dir>/out/example.png"
```

Use `examples/minimal_engineering_drawing/generate.py` as the compact reference implementation when a full scaffold is unnecessary.

## Debug Workflow

1. Reproduce with the smallest drawing input that still shows the defect.
2. **Compare embedded preview and external CAD output. If they differ, fix preview rendering before changing DXF geometry.**
3. Instrument bbox, chosen scales, anchors, and translate vectors temporarily. Remove instrumentation before delivery.
4. Add focused tests for the broken layout rule, not only broad smoke checks.
5. Verify final output with DXF smoke statistics, PNG render, and manual visual inspection.
6. If a host app launches the generator, rebuild or refresh the host so it uses the edited generator.

## Acceptance

Do not accept a CAD component because the DXF is merely non-empty. Minimum evidence:

- Generated DXF exists and has plausible entity count, layer set, and bbox.
- The rendered PNG shows the expected page frame, views, dimensions, notes, and schedules.
- Manual inspection checks text legibility, overlaps, table/title-block collisions, clipped geometry, stale debug labels, and wrong scale labels.
- Preview-only defects are verified against an external CAD viewer or an equivalent independent renderer.
- The target project can run the generator without hard-coded personal paths.

## Guardrails

- Do not hard-code drive letters, user directories, private project names, or one-off temp paths.
- Do not ship temporary debug logs or instrumentation hooks.
- Do not move downstream views or anchor columns to hide an upstream bbox or slot bug unless the layout contract explicitly allows it.
- Do not base scale selection on unrelated panels, tables, or title blocks.
- Do not compensate for preview renderer bugs by distorting the exported DXF geometry.
