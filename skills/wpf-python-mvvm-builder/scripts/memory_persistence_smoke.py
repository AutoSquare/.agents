# -*- coding: utf-8 -*-
"""Run smoke driver and write memory session_snapshot.json (WPF-free persist check)."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent

# Fixed sample WindowPlacement for verify --require-window-settings
SMOKE_WINDOW_SETTINGS = {
    "windowWidth": 960.0,
    "windowHeight": 540.0,
    "windowLeft": 120.0,
    "windowTop": 80.0,
    "windowState": "Normal",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--abbr", required=True)
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--display-name", default="Application")
    parser.add_argument(
        "--include-form-demo",
        action="store_true",
        help="Seed dataTables 测试表单 for verify --require-form-demo",
    )
    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()
    abbr = args.abbr.strip()
    app_id = args.app_id.strip()
    py_folder = project_dir / f"{abbr}Py"
    env_dir = project_dir / f"{abbr}Env"
    driver = py_folder / "CalculateDriver.py"
    py_exe = env_dir / "Scripts" / "python.exe"
    if not py_exe.is_file():
        py_exe = env_dir / "bin" / "python"
    if not driver.is_file() or not py_exe.is_file():
        print("Missing ASPy driver or ASEnv — run scaffold --apply first", file=sys.stderr)
        sys.exit(1)

    workspace = Path(tempfile.mkdtemp(prefix=f"{abbr}Work_persist_"))
    try:
        data_dir = workspace / "数据表"
        mat_dir = workspace / "材料库"
        data_dir.mkdir(parents=True)
        mat_dir.mkdir(parents=True)
        baseline = project_dir / "Assets" / "Baseline"
        seed = baseline / "DataTable" / "项目基本信息.json"
        if seed.is_file():
            shutil.copy(seed, data_dir / "项目基本信息.json")
        else:
            (data_dir / "项目基本信息.json").write_text(
                json.dumps([{"键": "app", "值": args.display_name}], ensure_ascii=False),
                encoding="utf-8",
            )
        env = os.environ.copy()
        env_var = f"{abbr.upper()}_WORKSPACE"
        env[env_var] = str(workspace)
        proc = subprocess.run(
            [str(py_exe), "-u", str(driver)],
            input=str(workspace) + "\n",
            text=True,
            capture_output=True,
            cwd=str(py_folder),
            env=env,
        )
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            sys.exit(proc.returncode)
        data_tables: dict[str, str] = {}
        material_tables: dict[str, str] = {}
        for file in data_dir.glob("*.json"):
            data_tables[file.stem] = file.read_text(encoding="utf-8")
        for file in mat_dir.glob("*.json"):
            material_tables[file.stem] = file.read_text(encoding="utf-8")
        if args.include_form_demo:
            data_tables["测试表单"] = json.dumps(
                {
                    "projectName": "smoke-form-demo",
                    "ownerName": "maintainer",
                    "memo": "memory_persistence_smoke seed",
                    "contactPhone": "13800000000",
                    "department": "测试部",
                    "siteAddress": "成都市高新区",
                },
                ensure_ascii=False,
                indent=2,
            )
        snap_dir = Path(os.environ.get("APPDATA", "")) / app_id
        snap_dir.mkdir(parents=True, exist_ok=True)
        snap_path = snap_dir / "session_snapshot.json"
        status_text = f"样本计算完成（smoke）\n{snap_path}"
        payload = {
            "formatVersion": 1,
            "displayName": args.display_name,
            "dataTables": data_tables,
            "materialTables": material_tables,
            "uiState": {"statusText": status_text},
        }
        tmp = snap_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(snap_path)
        settings_path = snap_dir / "user_settings.json"
        settings_tmp = settings_path.with_suffix(".json.tmp")
        settings_tmp.write_text(
            json.dumps(SMOKE_WINDOW_SETTINGS, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        settings_tmp.replace(settings_path)
        print(f"OK wrote {snap_path}")
        print(f"OK wrote {settings_path}")
        if "样本计算结果" not in data_tables:
            print("WARN: 样本计算结果 not in workspace", file=sys.stderr)
            sys.exit(1)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    main()
