# -*- coding: utf-8 -*-
"""Orchestrate AgentStatistics archive E2E (audit + verify + build; no memory reset)."""
from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL_ROOT / "scripts"
MARKER = ".dual-stack-persistence.json"


def read_marker(project_dir: Path) -> dict:
    path = project_dir / MARKER
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def find_sample_archive(project_dir: Path, ext: str) -> Path | None:
    if not ext.startswith("."):
        ext = "." + ext
    sample = project_dir / f"sample_import{ext}"
    if sample.is_file():
        return sample
    candidates = sorted(project_dir.glob(f"*{ext}"))
    return candidates[0] if candidates else None


def run(cmd: list[str], label: str) -> int:
    print(f"+ {label}")
    print("  ", " ".join(cmd))
    return subprocess.call(cmd)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--abbr", default="AS")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-launch-smoke", action="store_true")
    parser.add_argument(
        "--archive-path",
        default="",
        help="Override archive zip for verify (default: sample_import{Ext} or first *{Ext})",
    )
    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()
    abbr = args.abbr.strip()
    marker = read_marker(project_dir)
    ext = marker.get("ext", ".ast")
    prog_id = f"{marker.get('rootNamespace', 'App')}.ProjectFile"

    csproj = next(project_dir.glob("*.csproj"), None)
    if csproj is None:
        print("No .csproj in project-dir", file=sys.stderr)
        sys.exit(2)

    rc = run(
        [
            sys.executable,
            str(SCRIPTS / "audit_project.py"),
            "--project-dir",
            str(project_dir),
            "--abbr",
            abbr,
            "--expect",
            "archive",
        ],
        "audit --expect archive",
    )
    if rc != 0:
        sys.exit(rc)

    archive_path = Path(args.archive_path).resolve() if args.archive_path.strip() else find_sample_archive(project_dir, ext)
    if archive_path is None or not archive_path.is_file():
        print(f"No archive *{ext} found under {project_dir} — run migrate --import-last-snapshot first", file=sys.stderr)
        sys.exit(2)

    rc = run(
        [
            sys.executable,
            str(SCRIPTS / "verify_persistence_artifacts.py"),
            "--mode",
            "archive",
            "--archive-path",
            str(archive_path),
            "--require-form-demo",
        ],
        f"verify archive {archive_path.name}",
    )
    if rc != 0:
        sys.exit(rc)

    rc = run(
        [
            sys.executable,
            str(SCRIPTS / "smoke_bridge.py"),
            "--project-dir",
            str(project_dir),
            "--abbr",
            abbr,
        ],
        "smoke_bridge",
    )
    if rc != 0:
        sys.exit(rc)

    if not args.skip_build:
        rc = run(["dotnet", "build", str(csproj)], "dotnet build")
        if rc != 0:
            sys.exit(rc)

    if not args.skip_launch_smoke:
        exe_glob = str(project_dir / "bin" / "Debug" / "net8.0-windows" / "*.exe")
        matches = [p for p in glob.glob(exe_glob) if not p.lower().endswith("vshost.exe")]
        if matches:
            exe = Path(matches[0])
            proc = subprocess.Popen(
                [str(exe), str(archive_path)],
                cwd=str(exe.parent),
            )
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
            print(f"+ launch smoke: started {exe.name} with {archive_path.name} (terminated after timeout)")
        else:
            print("WARN: skip launch smoke — exe not found (build first?)")

    inspect = SCRIPTS / "inspect_file_association.py"
    if inspect.is_file():
        expected_exe = ""
        exe_glob = str(project_dir / "bin" / "Debug" / "net8.0-windows" / "*.exe")
        matches = [p for p in glob.glob(exe_glob) if not p.lower().endswith("vshost.exe")]
        if matches:
            expected_exe = matches[0]
        cmd = [
            sys.executable,
            str(inspect),
            "--ext",
            ext,
            "--prog-id",
            prog_id,
            "--check",
        ]
        if expected_exe:
            cmd.extend(["--expected-exe", expected_exe])
        rc = run(cmd, "inspect_file_association --check")
        if rc != 0:
            print("WARN: file association not synced — F5 once to register HKCU", file=sys.stderr)

    print("OK archive E2E orchestration complete")


if __name__ == "__main__":
    main()
