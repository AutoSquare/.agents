# -*- coding: utf-8 -*-
"""Create a portable Python environment in {Abbr}Env."""
from __future__ import annotations

import argparse
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

PYTHON_VERSION = "3.10.11"
EMBED_ZIP = f"python-{PYTHON_VERSION}-embed-amd64.zip"
EMBED_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/{EMBED_ZIP}"


def requirements_has_packages(requirements: Path) -> bool:
    if not requirements.is_file():
        return False
    for line in requirements.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return True
    return False


def download_embed_zip(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / EMBED_ZIP
    if target.is_file():
        return target
    print(f"download: {EMBED_URL}")
    urllib.request.urlretrieve(EMBED_URL, target)
    return target


def write_pth(env_dir: Path, abbr: str) -> None:
    pth_files = list(env_dir.glob("python*._pth"))
    if not pth_files:
        raise SystemExit(f"No python*._pth found in {env_dir}")
    pth = pth_files[0]
    zip_name = f"python{PYTHON_VERSION.replace('.', '')[:3]}.zip"
    lines = [zip_name, ".", f"..\\{abbr}Py", "", "# Uncomment to run site.main() automatically", "#import site"]
    pth.write_text("\n".join(lines) + "\n", encoding="ascii")


def create_portable_env(project_dir: Path, abbr: str, requirements: Path, force: bool) -> None:
    env_dir = project_dir / f"{abbr}Env"
    if env_dir.exists():
        if (env_dir / "pyvenv.cfg").is_file():
            if not force:
                raise SystemExit(f"{env_dir} is a venv with pyvenv.cfg. Re-run with --force to replace it.")
        elif any(env_dir.iterdir()) and not force:
            print(f"Env already exists: {env_dir}")
            return
        shutil.rmtree(env_dir)
    env_dir.mkdir(parents=True, exist_ok=True)
    archive = download_embed_zip(project_dir / ".cache")
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(env_dir)
    write_pth(env_dir, abbr)
    if requirements_has_packages(requirements):
        raise SystemExit(
            "Portable embeddable Python does not install requirements automatically. "
            f"Vendor dependencies into {abbr}Env or keep requirements empty."
        )
    py = env_dir / "python.exe"
    if not py.is_file():
        raise SystemExit(f"python.exe not found in {env_dir}")
    print(f"OK env={env_dir} python={py} version={PYTHON_VERSION}")


def copy_portable_env(source: Path, project_dir: Path, abbr: str, force: bool) -> None:
    if not source.is_dir():
        raise SystemExit(f"Portable env source not found: {source}")
    env_dir = project_dir / f"{abbr}Env"
    if env_dir.exists():
        if not force:
            raise SystemExit(f"Env already exists: {env_dir}; use --force to replace it.")
        shutil.rmtree(env_dir)
    shutil.copytree(source, env_dir, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pyvenv.cfg"))
    write_pth(env_dir, abbr)
    print(f"Copied portable env to {env_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--abbr", required=True)
    parser.add_argument(
        "--portable-source",
        default="",
        help="Optional existing portable Python directory to copy into {Abbr}Env.",
    )
    parser.add_argument(
        "--requirements",
        default="",
        help="requirements.txt path; default {Abbr}Py/requirements.txt under project.",
    )
    parser.add_argument("--force", action="store_true", help="Replace existing {Abbr}Env.")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    abbr = args.abbr.strip()
    req = Path(args.requirements).resolve() if args.requirements else project_dir / f"{abbr}Py" / "requirements.txt"
    if args.portable_source.strip():
        copy_portable_env(Path(args.portable_source).resolve(), project_dir, abbr, args.force)
    else:
        create_portable_env(project_dir, abbr, req, args.force)


if __name__ == "__main__":
    main()
