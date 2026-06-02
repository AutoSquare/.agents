# -*- coding: utf-8 -*-
"""
Inspect / migrate / purge %AppData%/{AppId} memory cache.

Agent workflow (not WPF runtime):
  1. --check → JSON report; if legacy/corrupt, ask the user explicitly (ours? migrate or purge)
  2. --migrate --apply → rewrite session_snapshot.json to current format
  3. --purge --apply → delete entire AppData/{AppId} directory
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from snapshot_table_codec import (  # noqa: E402
    CURRENT_SNAPSHOT_FORMAT_VERSION,
    looks_legacy_or_corrupt,
    migrate_snapshot_dict,
)


def appdata_dir(app_id: str) -> Path:
    return Path(os.environ.get("APPDATA", "")) / app_id


def check_cache(app_id: str) -> dict:
    root = appdata_dir(app_id)
    snap_path = root / "session_snapshot.json"
    settings_path = root / "user_settings.json"
    report: dict = {
        "appId": app_id,
        "directory": str(root),
        "exists": root.is_dir(),
        "snapshotPath": str(snap_path),
        "snapshotExists": snap_path.is_file(),
        "settingsExists": settings_path.is_file(),
        "status": "missing",
        "issues": [],
        "formatVersion": None,
        "actionRequired": False,
        "agentPrompt": "",
    }
    if not snap_path.is_file():
        report["status"] = "missing"
        report["agentPrompt"] = "无 session_snapshot.json；首次运行将自动创建。"
        return report

    try:
        text = snap_path.read_text(encoding="utf-8-sig")
        snapshot = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        report["status"] = "corrupt"
        report["issues"] = [f"snapshot parse error: {exc}"]
        report["actionRequired"] = True
        report["agentPrompt"] = (
            f"发现无法解析的快照：{snap_path}。"
            "请向用户确认是否为本软件（AppId={app_id}）数据；"
            "是则选择 --migrate（转当前 memory 格式）或 --purge（删除整个缓存目录）。"
        )
        return report

    report["formatVersion"] = snapshot.get("formatVersion")
    issues = looks_legacy_or_corrupt(snapshot)
    report["issues"] = issues
    if issues:
        report["status"] = "legacy"
        report["actionRequired"] = True
        report["agentPrompt"] = (
            f"发现旧版或损坏缓存（{snap_path}）：{'; '.join(issues)}。"
            "请向用户确认是否为本软件数据；"
            "是则 --migrate --apply 迁移为当前 memory 格式，或 --purge --apply 删除整个 AppData 目录后重建。"
        )
    else:
        report["status"] = "ok"
        report["agentPrompt"] = "缓存格式正常，可继续 scaffold / E2E。"
    return report


def migrate_cache(app_id: str, display_name: str, dry_run: bool) -> list[str]:
    root = appdata_dir(app_id)
    snap_path = root / "session_snapshot.json"
    actions: list[str] = []
    if not snap_path.is_file():
        actions.append("no snapshot — skip migrate")
        return actions
    snapshot = json.loads(snap_path.read_text(encoding="utf-8-sig"))
    normalized = migrate_snapshot_dict(snapshot, display_name=display_name)
    actions.append(f"normalize formatVersion → {CURRENT_SNAPSHOT_FORMAT_VERSION}")
    actions.append(f"rewrite {snap_path}")
    if not dry_run:
        root.mkdir(parents=True, exist_ok=True)
        tmp = snap_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(snap_path)
    return actions


def purge_cache(app_id: str, dry_run: bool) -> list[str]:
    root = appdata_dir(app_id)
    actions: list[str] = []
    if not root.is_dir():
        actions.append("cache directory missing — skip purge")
        return actions
    actions.append(f"remove {root}")
    if not dry_run:
        shutil.rmtree(root, ignore_errors=True)
    return actions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--display-name", default="Application")
    parser.add_argument("--check", action="store_true", help="Print JSON report for Agent intake.")
    parser.add_argument("--migrate", action="store_true", help="Rewrite snapshot to current memory format.")
    parser.add_argument("--purge", action="store_true", help="Delete entire AppData/{AppId} directory.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    app_id = args.app_id.strip()

    if args.check:
        report = check_cache(app_id)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if report["actionRequired"]:
            sys.exit(10)
        sys.exit(0)

    if args.migrate or args.purge:
        if not args.dry_run and not args.apply:
            print("Specify --dry-run or --apply", file=sys.stderr)
            sys.exit(2)
        dry_run = args.dry_run and not args.apply
        if args.purge:
            for a in purge_cache(app_id, dry_run=dry_run):
                print(a)
        elif args.migrate:
            for a in migrate_cache(app_id, args.display_name, dry_run=dry_run):
                print(a)
        print("OK")
        return

    parser.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()
