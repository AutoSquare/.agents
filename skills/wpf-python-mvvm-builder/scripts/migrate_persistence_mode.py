# -*- coding: utf-8 -*-
"""Migrate between memory and archive persistence modes."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
MARKER = ".dual-stack-persistence.json"


def read_marker(project_dir: Path) -> dict:
    path = project_dir / MARKER
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_snapshot_tables(project_dir: Path, app_id: str) -> dict | None:
    import os

    appdata = Path(os.environ.get("APPDATA", ""))
    snap = appdata / app_id / "session_snapshot.json"
    if not snap.is_file():
        return None
    return json.loads(snap.read_text(encoding="utf-8-sig"))


def import_snapshot_to_archive(project_dir: Path, app_id: str, ext: str, dry_run: bool) -> list[str]:
    actions: list[str] = []
    snap = load_snapshot_tables(project_dir, app_id)
    if not snap:
        actions.append("no session_snapshot.json — skip import")
        return actions
    sample_path = project_dir / f"sample_import{ext}"
    actions.append(f"would create {sample_path.name} from snapshot")
    if dry_run:
        return actions
    # After scaffold, user builds ProjectDocument via inline C# — we write JSON tables to temp zip via Python zipfile
    import zipfile
    from datetime import datetime, timezone

    data_tables = snap.get("dataTables", {})
    material_tables = snap.get("materialTables", {})
    manifest = json.dumps(
        {
            "formatVersion": 1,
            "appId": app_id,
            "displayName": snap.get("displayName", "Imported"),
            "createdUtc": datetime.now(timezone.utc).isoformat(),
        },
        ensure_ascii=False,
    )
    with zipfile.ZipFile(sample_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", manifest)
        for name, body in data_tables.items():
            zf.writestr(f"数据表/{name}.json", body if isinstance(body, str) else json.dumps(body, ensure_ascii=False))
        for name, body in material_tables.items():
            zf.writestr(f"材料库/{name}.json", body if isinstance(body, str) else json.dumps(body, ensure_ascii=False))
    actions.append(f"created {sample_path.name}")
    return actions


def export_archive_to_snapshot(project_dir: Path, ext: str, app_id: str, dry_run: bool) -> list[str]:
    actions: list[str] = []
    # Find most recent ext file in project dir (user may have saved)
    candidates = list(project_dir.glob(f"*{ext}"))
    if not candidates:
        actions.append(f"no *{ext} in project — skip archive export")
        return actions
    archive_path = candidates[0]
    actions.append(f"read tables from {archive_path.name}")
    if dry_run:
        return actions
    import zipfile

    data_tables: dict[str, str] = {}
    material_tables: dict[str, str] = {}
    display = "Migrated"
    with zipfile.ZipFile(archive_path, "r") as zf:
        for name in zf.namelist():
            if name == "manifest.json":
                manifest = json.loads(zf.read(name).decode("utf-8"))
                display = manifest.get("displayName", display)
                continue
            parts = name.replace("\\", "/").split("/")
            if len(parts) != 2:
                continue
            folder, file = parts
            table = file.replace(".json", "")
            body = zf.read(name).decode("utf-8")
            if folder == "数据表":
                data_tables[table] = body
            elif folder == "材料库":
                material_tables[table] = body
    snap = {
        "formatVersion": 1,
        "displayName": display,
        "dataTables": data_tables,
        "materialTables": material_tables,
        "uiState": {},
    }
    import os

    dest_dir = Path(os.environ.get("APPDATA", "")) / app_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "session_snapshot.json"
    tmp = dest.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(dest)
    actions.append(f"wrote {dest}")
    return actions


def run_scaffold(project_dir: Path, abbr: str, to_mode: str, marker: dict, apply: bool, include_form_demo: bool = False) -> int:
    cmd = [
        sys.executable,
        str(SKILL_ROOT / "scripts" / "scaffold_dual_stack.py"),
        "--project-dir",
        str(project_dir),
        "--abbr",
        abbr,
        "--root-namespace",
        marker.get("rootNamespace", "App"),
        "--display-name",
        marker.get("displayName", "Application"),
        "--persistence",
        to_mode,
        "--migrate-to",
        to_mode,
    ]
    if to_mode == "archive":
        cmd.extend(["--ext", marker.get("ext", ".proj")])
    else:
        cmd.extend(["--app-id", marker.get("appId", marker.get("rootNamespace", "App"))])
    if include_form_demo:
        cmd.append("--include-form-demo")
    if apply:
        cmd.append("--apply")
    else:
        cmd.append("--dry-run")
    print("+", " ".join(cmd))
    return subprocess.call(cmd)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--abbr", required=True)
    parser.add_argument("--from", dest="from_mode", required=True, choices=("memory", "archive"))
    parser.add_argument("--to", dest="to_mode", required=True, choices=("memory", "archive"))
    parser.add_argument("--import-last-snapshot", action="store_true")
    parser.add_argument("--ext", default="", help="Archive extension when migrating to archive (e.g. .asproj).")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.from_mode == args.to_mode:
        print("from and to must differ", file=sys.stderr)
        sys.exit(2)
    if not args.dry_run and not args.apply:
        print("Specify --dry-run or --apply", file=sys.stderr)
        sys.exit(2)

    project_dir = Path(args.project_dir).resolve()
    dry_run = args.dry_run and not args.apply
    marker = read_marker(project_dir)
    marker.setdefault("abbr", args.abbr)
    marker.setdefault("ext", ".proj")
    marker.setdefault("appId", marker.get("rootNamespace", "App"))
    if args.ext:
        ext = args.ext.strip()
        if not ext.startswith("."):
            ext = "." + ext
        marker["ext"] = ext
    actions: list[str] = []

    if args.from_mode == "memory" and args.to_mode == "archive":
        if args.import_last_snapshot:
            actions.extend(import_snapshot_to_archive(project_dir, marker["appId"], marker["ext"], dry_run))
    elif args.from_mode == "archive" and args.to_mode == "memory":
        actions.extend(export_archive_to_snapshot(project_dir, marker["ext"], marker["appId"], dry_run))

    rc = run_scaffold(
        project_dir,
        args.abbr,
        args.to_mode,
        marker,
        apply=not dry_run,
        include_form_demo=bool(marker.get("formDemo")),
    )
    print("migrate actions:")
    for a in actions:
        print(f"  * {a}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
