# Layout Case Studies

Anonymous production lessons behind this skill. Use as transferable patterns, not as code to copy verbatim.

## Case 1: Independent Scale Budgets

Problem: the `mainBand` elevation drawings became tiny because `secondaryPanel` / `scheduleTable` width leaked into the main scale solver.

Portable rule: solve scale per independent view band. Couple budgets only when the drawing specification explicitly requires it.

See: `layout-engine.md` — Scale Selection.

## Case 2: Adjacent View Slots

Problem: moving `middleView` to avoid overlap accidentally shifted a fixed `downstreamAnchor` column and broke the right side of the drawing.

Portable rule: keep downstream anchors fixed when the contract says they are fixed. Move a view only within its allowed slot, and test both neighbor clearances.

See: `layout-engine.md` — Fixed Downstream Anchor, Slot Placement with Baseline Floor.

## Case 3: Stacked Details

Problem: three vertically stacked views in `detailStack` overlapped because placement used planned geometry centers and ignored captions/dimensions.

Portable rule: draw or estimate each band, measure actual paper bbox, then top-align and distribute slack by actual bbox height.

See: `layout-engine.md` — Top-Align Chain Reflow; `anti-patterns.md` — Planned geometry center.

## Case 4: Schedule/Table Placement

Problem: a `scheduleTable` appeared outside or was clipped because the decision used a narrow-column width check and then a global translate moved the table again.

Portable rule: table feasibility must check right alignment, vertical stack, notes/title-block clearance, and translate membership. Outside tables are fixed by policy and excluded from main-band translate.

See: `layout-engine.md` — Table Anchors.

## Case 5: Preview vs Output

Problem: embedded preview differed from external CAD because text height and polyline width were rendered differently.

Portable rule: validate generator and viewer separately. If the exported DXF is correct in an external viewer, fix preview entity rendering instead of changing geometry.

See: `viewer-integration.md`; `SKILL.md` — Debug Workflow step 2.

## Case 6: Environment

Problem: fixes appeared ineffective because of stale host builds, file locks, or workspace/input confusion.

Portable rule: document the generator launch contract, close external CAD locks before overwriting output, and rebuild or refresh the host after generator/viewer changes.

See: `cad-system-architecture.md` — Host integration.
