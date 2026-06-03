# -*- coding: utf-8 -*-
"""Smoke test: run CalculateDriver against a synthetic workspace (no WPF UI)."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def resolve_python(project_dir: Path, abbr: str) -> Path:
    env_dir = project_dir / f"{abbr}Env"
    candidates = (
        env_dir / "python.exe",
        env_dir / "Scripts" / "python.exe",
        env_dir / "bin" / "python",
    )
    return next((candidate for candidate in candidates if candidate.is_file()), candidates[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--abbr", required=True)
    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()
    abbr = args.abbr.strip()
    py_folder = project_dir / f"{abbr}Py"
    driver = py_folder / "CalculateDriver.py"
    py_exe = resolve_python(project_dir, abbr)
    if not driver.is_file():
        print(f"Missing driver: {driver}", file=sys.stderr)
        sys.exit(1)
    if not py_exe.is_file():
        print(
            f"Missing python: {py_exe} — run setup_python_env.py to create the portable {abbr}Env",
            file=sys.stderr,
        )
        sys.exit(1)

    workspace = Path(tempfile.mkdtemp(prefix=f"{abbr}Work_smoke_"))
    try:
        data_dir = workspace / "数据表"
        mat_dir = workspace / "材料库"
        data_dir.mkdir(parents=True)
        mat_dir.mkdir(parents=True)
        baseline = project_dir / "Assets" / "Baseline"
        if (baseline / "DataTable" / "项目基本信息.json").is_file():
            shutil.copy(baseline / "DataTable" / "项目基本信息.json", data_dir / "项目基本信息.json")
        else:
            (data_dir / "项目基本信息.json").write_text(
                json.dumps([{"键": "app", "值": "smoke"}], ensure_ascii=False),
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
        print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        result_file = data_dir / "样本计算结果.json"
        if proc.returncode != 0:
            sys.exit(proc.returncode)
        if not result_file.is_file():
            print("Missing 样本计算结果.json", file=sys.stderr)
            sys.exit(1)
        print(f"OK smoke workspace={workspace}")
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    main()
