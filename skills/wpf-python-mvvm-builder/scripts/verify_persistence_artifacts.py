# -*- coding: utf-8 -*-
"""Verify persistence artifact files (snapshot or archive zip)."""
from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from snapshot_table_codec import (  # noqa: E402
    FORM_DEMO_TABLE,
    load_snapshot_tables,
    looks_legacy_or_corrupt,
    parse_form_demo,
    table_json_parseable,
)

WINDOW_SETTING_KEYS = (
    "windowWidth",
    "windowHeight",
    "windowLeft",
    "windowTop",
    "windowState",
)


def check_memory_snapshot(
    app_id: str,
    require_result_table: bool = False,
    require_ui_state: bool = False,
    require_form_demo: bool = False,
    require_roundtrip: bool = True,
) -> list[str]:
    errors: list[str] = []
    appdata = Path(os.environ.get("APPDATA", ""))
    snap = appdata / app_id / "session_snapshot.json"
    if not snap.is_file():
        errors.append(f"missing {snap}")
        return errors
    text = snap.read_text(encoding="utf-8-sig")
    data = json.loads(text)
    for key in ("dataTables", "materialTables"):
        if key not in data:
            errors.append(f"snapshot missing key: {key}")

    if require_roundtrip:
        legacy = looks_legacy_or_corrupt(data)
        errors.extend(f"snapshot roundtrip: {issue}" for issue in legacy)
        data_tables, material_tables = load_snapshot_tables(data)
        for name, payload in {**data_tables, **material_tables}.items():
            if not table_json_parseable(payload):
                errors.append(f"table {name} not valid JSON after normalize")

    if require_result_table:
        tables = data.get("dataTables", {})
        if "样本计算结果" not in tables:
            errors.append("snapshot dataTables missing 样本计算结果")
    if require_ui_state:
        ui_state = data.get("uiState")
        if not isinstance(ui_state, dict):
            errors.append("snapshot missing uiState object")
        else:
            status = ui_state.get("statusText")
            if not isinstance(status, str) or not status.strip():
                errors.append("snapshot uiState.statusText missing or empty")
    if require_form_demo:
        data_tables, _ = load_snapshot_tables(data)
        if FORM_DEMO_TABLE not in data_tables:
            errors.append(f"snapshot dataTables missing {FORM_DEMO_TABLE}")
        elif parse_form_demo(data_tables[FORM_DEMO_TABLE]) is None:
            errors.append(f"{FORM_DEMO_TABLE} not parseable as form demo object")
    return errors


def check_memory_window_settings(app_id: str) -> list[str]:
    errors: list[str] = []
    appdata = Path(os.environ.get("APPDATA", ""))
    settings_path = appdata / app_id / "user_settings.json"
    if not settings_path.is_file():
        errors.append(f"missing {settings_path}")
        return errors
    text = settings_path.read_text(encoding="utf-8-sig")
    data = json.loads(text)
    for key in WINDOW_SETTING_KEYS:
        if key not in data:
            errors.append(f"user_settings missing key: {key}")
    return errors


def check_archive_file(
    path: Path,
    require_result_table: bool = False,
    require_form_demo: bool = False,
) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        errors.append(f"missing archive: {path}")
        return errors
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        if "manifest.json" not in names:
            errors.append("archive missing manifest.json")
        has_data = any(n.startswith("数据表/") for n in names)
        if not has_data:
            errors.append("archive missing 数据表/")
        form_entry = "数据表/测试表单.json"
        result_entry = "数据表/样本计算结果.json"
        if require_result_table and result_entry not in names:
            errors.append(f"archive missing {result_entry}")
        if require_form_demo:
            if form_entry not in names:
                errors.append(f"archive missing {form_entry}")
            elif form_entry in names:
                body = zf.read(form_entry).decode("utf-8-sig")
                if parse_form_demo(body) is None:
                    errors.append(f"{form_entry} not parseable as form demo object")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=("memory", "archive"))
    parser.add_argument("--app-id", default="")
    parser.add_argument("--archive-path", default="")
    parser.add_argument(
        "--require-sample-result",
        action="store_true",
        help="memory/archive: assert 样本计算结果 table exists",
    )
    parser.add_argument(
        "--require-ui-state",
        action="store_true",
        help="memory: assert uiState.statusText is non-empty",
    )
    parser.add_argument(
        "--require-window-settings",
        action="store_true",
        help="memory: assert user_settings.json has WindowPlacement keys",
    )
    parser.add_argument(
        "--require-form-demo",
        action="store_true",
        help="memory/archive: assert 测试表单 exists and is parseable",
    )
    parser.add_argument(
        "--skip-roundtrip",
        action="store_true",
        help="memory: skip legacy/corrupt table normalize checks",
    )
    args = parser.parse_args()
    errors: list[str] = []
    if args.mode == "memory":
        app_id = args.app_id.strip()
        if not app_id:
            print("--app-id required for memory mode", file=sys.stderr)
            sys.exit(2)
        errors = check_memory_snapshot(
            app_id,
            require_result_table=args.require_sample_result,
            require_ui_state=args.require_ui_state,
            require_form_demo=args.require_form_demo,
            require_roundtrip=not args.skip_roundtrip,
        )
        if args.require_window_settings:
            errors.extend(check_memory_window_settings(app_id))
    else:
        if not args.archive_path.strip():
            print("--archive-path required for archive mode", file=sys.stderr)
            sys.exit(2)
        errors = check_archive_file(
            Path(args.archive_path).resolve(),
            require_result_table=args.require_sample_result,
            require_form_demo=args.require_form_demo,
        )
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("OK persistence artifact verified")


if __name__ == "__main__":
    main()
