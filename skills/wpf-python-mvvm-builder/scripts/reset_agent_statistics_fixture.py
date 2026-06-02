# -*- coding: utf-8 -*-
"""Reset AgentStatistics (or any project) to VS empty WPF fixture baseline."""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
BASELINE = SKILL_ROOT / "examples" / "fixture-baseline" / "agent-statistics"

BASELINE_FILES = (
    "AgentStatistics.csproj",
    "App.xaml",
    "App.xaml.cs",
    "MainWindow.xaml",
    "MainWindow.xaml.cs",
    "AssemblyInfo.cs",
)

REMOVE_DIRS = (
    "ViewModel",
    "Services",
    "Model",
    "Themes",
    "Resources",
    "Properties",
    "Assets",
)

REMOVE_FILES = (
    "CompositionRoot.cs",
    "CompositionRoot.ViewModels.cs",
    "ApplicationBootstrap.cs",
    ".dual-stack-persistence.json",
)

REMOVE_GLOBS = ("*Py", "*Env")

DUAL_STACK_CSproj_PATTERN = re.compile(
    r"\n?\s*<!-- dual-stack:.*?-->(?:\s*\n\s*<ItemGroup>.*?</ItemGroup>)*",
    re.DOTALL,
)


def strip_csproj_dual_stack(text: str) -> str:
    while True:
        new_text = DUAL_STACK_CSproj_PATTERN.sub("\n", text, count=1)
        if new_text == text:
            break
        text = new_text
    return re.sub(r"\n{3,}", "\n\n", text)


def strip_gitignore_dual_stack(gi: Path) -> None:
    if not gi.is_file():
        return
    lines = []
    for line in gi.read_text(encoding="utf-8").splitlines():
        if "Env/" in line or "Work_*" in line or "dual-stack" in line.lower():
            continue
        if line.strip().startswith("#") and "Abbr" in line:
            continue
        lines.append(line)
    gi.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.dry_run and not args.apply:
        print("Specify --dry-run or --apply", file=sys.stderr)
        sys.exit(2)

    project_dir = Path(args.project_dir).resolve()
    dry_run = args.dry_run and not args.apply
    actions: list[str] = []

    for name in BASELINE_FILES:
        src = BASELINE / name
        dest = project_dir / name
        if src.is_file():
            actions.append(f"restore {name}")
            if not dry_run:
                dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    for dname in REMOVE_DIRS:
        target = project_dir / dname
        if target.exists():
            actions.append(f"remove {dname}/")
            if not dry_run:
                shutil.rmtree(target, ignore_errors=True)

    for fname in REMOVE_FILES:
        target = project_dir / fname
        if target.is_file():
            actions.append(f"remove {fname}")
            if not dry_run:
                target.unlink()

    for child in project_dir.iterdir():
        if child.is_dir() and (child.name.endswith("Py") or child.name.endswith("Env")):
            actions.append(f"remove {child.name}/")
            if not dry_run:
                shutil.rmtree(child, ignore_errors=True)

    docs_dev = project_dir / "docs" / "开发说明.md"
    if docs_dev.is_file():
        actions.append("remove docs/开发说明.md")
        if not dry_run:
            docs_dev.unlink()

    for csproj in project_dir.glob("*.csproj"):
        text = csproj.read_text(encoding="utf-8")
        if "dual-stack:" in text:
            actions.append(f"strip dual-stack from {csproj.name}")
            if not dry_run:
                csproj.write_text(strip_csproj_dual_stack(text), encoding="utf-8")

    gi = project_dir / ".gitignore"
    if gi.is_file() and ("Env/" in gi.read_text(encoding="utf-8")):
        actions.append("strip dual-stack .gitignore")
        if not dry_run:
            strip_gitignore_dual_stack(gi)

    print(f"mode={'dry-run' if dry_run else 'apply'}")
    print(f"project={project_dir}")
    for a in actions:
        print(f"  * {a}")
    print("OK")


if __name__ == "__main__":
    main()
