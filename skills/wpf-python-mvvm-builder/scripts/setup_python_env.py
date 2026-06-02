# -*- coding: utf-8 -*-
"""Create or copy Python environment into {Abbr}Env."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent


def find_python() -> str:
    for cmd in ("py -3", "python3", "python"):
        try:
            parts = cmd.split()
            r = subprocess.run([*parts, "--version"], capture_output=True, text=True, check=False)
            if r.returncode == 0:
                return cmd
        except OSError:
            continue
    raise SystemExit("No Python launcher found (py -3 / python).")


def run_cmd(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def create_venv(env_dir: Path, requirements: Path) -> None:
    if env_dir.exists():
        if any(env_dir.iterdir()):
            print(f"Env already exists: {env_dir}")
            return
    env_dir.parent.mkdir(parents=True, exist_ok=True)
    launcher = find_python()
    parts = launcher.split()
    run_cmd([*parts, "-m", "venv", str(env_dir)])
    py = env_dir / "Scripts" / "python.exe"
    if not py.is_file():
        py = env_dir / "bin" / "python"
    if requirements.is_file():
        run_cmd([str(py), "-m", "pip", "install", "-r", str(requirements)])


def copy_conda_env(conda_prefix: Path, env_dir: Path) -> None:
    if not conda_prefix.is_dir():
        raise SystemExit(f"Conda prefix not found: {conda_prefix}")
    if env_dir.exists():
        shutil.rmtree(env_dir)
    shutil.copytree(conda_prefix, env_dir, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"Copied conda env to {env_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--abbr", required=True)
    parser.add_argument("--conda", default="", help="Path to existing conda env prefix to copy.")
    parser.add_argument(
        "--requirements",
        default="",
        help="requirements.txt path; default {Abbr}Py/requirements.txt under project.",
    )
    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()
    abbr = args.abbr.strip()
    env_dir = project_dir / f"{abbr}Env"
    req = Path(args.requirements) if args.requirements else project_dir / f"{abbr}Py" / "requirements.txt"
    if not req.is_file():
        req = SKILL_ROOT / "templates" / "python" / "requirements.txt"

    if args.conda.strip():
        copy_conda_env(Path(args.conda).resolve(), env_dir)
    else:
        create_venv(env_dir, req)
    py = env_dir / "Scripts" / "python.exe"
    if not py.is_file():
        py = env_dir / "bin" / "python"
    if not py.is_file():
        print("WARN: python executable not found in env dir", file=sys.stderr)
        sys.exit(1)
    print(f"OK env={env_dir} python={py}")


if __name__ == "__main__":
    main()
