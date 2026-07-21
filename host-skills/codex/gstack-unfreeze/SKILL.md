---
name: unfreeze
description: |
  Clear the freeze boundary set by /freeze, allowing edits to all directories
  again. Use when you want to widen edit scope without ending the session.
  Use when asked to "unfreeze", "unlock edits", "remove freeze", or
  "allow all edits". (gstack)
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

## Portable `.agents` compatibility

This bundle intentionally omits overlapping gstack entries. When this workflow names an omitted command, use the existing equivalent: `investigate` -> `systematic-debugging` or `diagnose`; `review` -> `requesting-code-review`; `ship` -> `finishing-a-development-branch`; `spec` -> `to-prd` + `to-issues`; `context-save`/`context-restore` -> `handoff`; planning/office-hours/design consultation -> the installed brainstorming, planning, grill, architecture, prototype, and UI/UX skills. `gstack-upgrade` and gbrain setup/sync are not managed here. On Windows, run Bash blocks with Git Bash (`C:\Program Files\Git\bin\bash.exe`) when `bash` is not on PATH.

# /unfreeze — Clear Freeze Boundary

Remove the edit restriction set by `/freeze`, allowing edits to all directories.

```bash
mkdir -p ~/.gstack/analytics
echo '{"skill":"unfreeze","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
```

## Clear the boundary

```bash
eval "$($GSTACK_ROOT/bin/gstack-paths)"
STATE_DIR="$GSTACK_STATE_ROOT"
if [ -f "$STATE_DIR/freeze-dir.txt" ]; then
  PREV=$(cat "$STATE_DIR/freeze-dir.txt")
  rm -f "$STATE_DIR/freeze-dir.txt"
  echo "Freeze boundary cleared (was: $PREV). Edits are now allowed everywhere."
else
  echo "No freeze boundary was set."
fi
```

Tell the user the result. Note that `/freeze` hooks are still registered for the
session — they will just allow everything since no state file exists. To re-freeze,
run `/freeze` again.
