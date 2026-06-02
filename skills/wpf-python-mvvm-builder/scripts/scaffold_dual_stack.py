# -*- coding: utf-8 -*-
"""Scaffold WPF + Python dual-stack MVVM with shell + persistence mode."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_ROOT / "templates"
BASELINE = SKILL_ROOT / "examples" / "fixture-baseline" / "agent-statistics"

APP_RESOURCES_BLOCK = """
    <Application.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <ResourceDictionary Source="/Themes/DefaultTheme.xaml"/>
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </Application.Resources>"""

CSPROJ_PACKAGES = """
  <!-- dual-stack: packages -->
  <ItemGroup>
    <PackageReference Include="CommunityToolkit.Mvvm" Version="8.4.0" />
    <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="9.0.0" />
  </ItemGroup>
"""

CSPROJ_RESOURCES = """
  <!-- dual-stack: resources -->
  <ItemGroup>
    <None Remove="Resources\\**\\*" />
  </ItemGroup>
  <ItemGroup>
    <Resource Include="Resources\\**\\*" Exclude="Resources\\**\\*.cs" />
  </ItemGroup>
"""

CSPROJ_PROPERTIES = """
  <!-- dual-stack: properties -->
  <ItemGroup>
    <Compile Update="Properties\\Resource.Designer.cs">
      <DesignTime>True</DesignTime>
      <AutoGen>True</AutoGen>
      <DependentUpon>Resource.resx</DependentUpon>
    </Compile>
    <Compile Update="Properties\\Settings.Designer.cs">
      <DesignTimeSharedInput>True</DesignTimeSharedInput>
      <AutoGen>True</AutoGen>
      <DependentUpon>Settings.settings</DependentUpon>
    </Compile>
  </ItemGroup>
  <ItemGroup>
    <EmbeddedResource Update="Properties\\Resource.resx">
      <Generator>PublicResXFileCodeGenerator</Generator>
      <LastGenOutput>Resource.Designer.cs</LastGenOutput>
    </EmbeddedResource>
    <None Update="Properties\\Settings.settings">
      <Generator>SettingsSingleFileGenerator</Generator>
      <LastGenOutput>Settings.Designer.cs</LastGenOutput>
    </None>
  </ItemGroup>
"""

CSPROJ_PY_ITEM = """
  <!-- dual-stack: {abbr}Py -->
  <ItemGroup>
    <None Update="{py_folder}/**/*.py">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </None>
  </ItemGroup>
"""

CSPROJ_ENV_ITEM = """
  <!-- dual-stack: {abbr}Env -->
  <ItemGroup>
    <Content Include="{env_folder}/**/*" Condition="Exists('{env_folder}')">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </Content>
  </ItemGroup>
"""

CSPROJ_BASELINE_ITEM = """
  <!-- dual-stack: baseline -->
  <ItemGroup>
    <Content Include="Assets/Baseline/**/*.json">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </Content>
  </ItemGroup>
"""

PERSISTENCE_MARKER = ".dual-stack-persistence.json"

ARCHIVE_ONLY_PATHS = [
    "Model/Persistence/ProjectVault.cs",
    "Services/ProjectFileService.cs",
]
MEMORY_ONLY_PATHS = [
    "Services/UserSettingsStore.cs",
    "Services/SessionSnapshotStore.cs",
]


def has_non_ascii_path_part(name: str) -> bool:
    return any(ord(c) > 127 for c in name)


def build_context(args: argparse.Namespace) -> dict[str, str]:
    abbr = args.abbr.strip()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]{0,15}", abbr):
        raise SystemExit("Abbr must be ASCII letters/digits, start with a letter, max 16 chars.")
    persistence = args.persistence.strip().lower()
    if persistence not in ("memory", "archive"):
        raise SystemExit("--persistence must be memory or archive")
    ext = (args.ext or ".proj").strip()
    if not ext.startswith("."):
        ext = "." + ext
    app_id = (args.app_id or args.root_namespace).strip()
    if persistence == "memory" and not app_id:
        raise SystemExit("--app-id required for memory mode")
    return {
        "Abbr": abbr,
        "AbbrUpper": abbr.upper(),
        "RootNamespace": args.root_namespace.strip(),
        "Ext": ext,
        "DisplayName": args.display_name,
        "PyFolder": f"{abbr}Py",
        "EnvFolder": f"{abbr}Env",
        "WorkspaceEnvVar": f"{abbr.upper()}_WORKSPACE",
        "PersistenceMode": persistence,
        "AppId": app_id,
    }


def substitute(text: str, ctx: dict[str, str]) -> str:
    for key, value in ctx.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def find_csproj(project_dir: Path) -> Path:
    for p in project_dir.glob("*.csproj"):
        t = p.read_text(encoding="utf-8")
        if "<UseWPF>true</UseWPF>" in t or "<UseWPF>True</UseWPF>" in t:
            return p
    csprojs = list(project_dir.glob("*.csproj"))
    if not csprojs:
        raise SystemExit("No .csproj in project-dir.")
    return csprojs[0]


def iter_template_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return [p for p in root.rglob("*") if p.is_file()]


def collect_template_writes(project_dir: Path, ctx: dict[str, str], include_form_demo: bool = False) -> list[tuple[Path, Path, str]]:
    writes: list[tuple[Path, Path, str]] = []
    mode = ctx["PersistenceMode"]

    for src in iter_template_files(TEMPLATES / "csharp"):
        rel = src.relative_to(TEMPLATES / "csharp")
        writes.append((src, project_dir / rel, substitute(src.read_text(encoding="utf-8"), ctx)))

    persist_root = TEMPLATES / "persistence" / mode
    for src in iter_template_files(persist_root):
        rel = src.relative_to(persist_root)
        writes.append((src, project_dir / rel, substitute(src.read_text(encoding="utf-8"), ctx)))

    for src in iter_template_files(TEMPLATES / "themes"):
        rel = src.relative_to(TEMPLATES / "themes")
        writes.append((src, project_dir / "Themes" / rel, src.read_text(encoding="utf-8")))

    for src in iter_template_files(TEMPLATES / "resources"):
        rel = src.relative_to(TEMPLATES / "resources")
        if src.suffix in (".md", ".txt") or src.name == ".gitkeep":
            content = src.read_text(encoding="utf-8")
        else:
            content = src.read_text(encoding="utf-8", errors="replace")
        writes.append((src, project_dir / "Resources" / rel, content))

    for src in iter_template_files(TEMPLATES / "properties"):
        rel = src.relative_to(TEMPLATES / "properties")
        writes.append((src, project_dir / "Properties" / rel, substitute(src.read_text(encoding="utf-8"), ctx)))

    py_dest = project_dir / ctx["PyFolder"]
    for src in (TEMPLATES / "python").glob("*"):
        if src.is_file():
            writes.append((src, py_dest / src.name, substitute(src.read_text(encoding="utf-8"), ctx)))

    if mode == "archive":
        assets = TEMPLATES / "assets" / "Baseline"
        for src in iter_template_files(assets):
            rel = src.relative_to(TEMPLATES / "assets")
            dest = project_dir / "Assets" / rel
            writes.append((src, dest, substitute(src.read_text(encoding="utf-8"), ctx)))

    doc_src = TEMPLATES / "docs" / "开发说明-模板.md"
    if doc_src.is_file():
        writes.append((doc_src, project_dir / "docs" / "开发说明.md", substitute(doc_src.read_text(encoding="utf-8"), ctx)))

    if include_form_demo and mode == "memory":
        for src in iter_template_files(TEMPLATES / "form-demo"):
            rel = src.relative_to(TEMPLATES / "form-demo")
            writes.append((src, project_dir / rel, substitute(src.read_text(encoding="utf-8"), ctx)))
    elif include_form_demo and mode == "archive":
        for src in iter_template_files(TEMPLATES / "form-demo-archive"):
            rel = src.relative_to(TEMPLATES / "form-demo-archive")
            writes.append((src, project_dir / rel, substitute(src.read_text(encoding="utf-8"), ctx)))

    marker = {
        "persistence": mode,
        "abbr": ctx["Abbr"],
        "ext": ctx["Ext"],
        "appId": ctx["AppId"],
        "rootNamespace": ctx["RootNamespace"],
        "displayName": ctx["DisplayName"],
        "formDemo": include_form_demo,
    }
    writes.append((doc_src, project_dir / PERSISTENCE_MARKER, json.dumps(marker, indent=2, ensure_ascii=False)))

    return writes


def is_empty_app_resources(app_xaml: Path) -> bool:
    if not app_xaml.is_file():
        return False
    text = app_xaml.read_text(encoding="utf-8")
    m = re.search(r"<Application\.Resources>(.*?)</Application\.Resources>", text, re.DOTALL)
    if not m:
        return False
    inner = m.group(1).strip()
    return inner == "" or inner == "<!-- -->"


def patch_app_xaml(project_dir: Path, dry_run: bool, persistence_mode: str = "memory") -> list[str]:
    app_path = project_dir / "App.xaml"
    if not app_path.is_file():
        return ["App.xaml missing"]
    text = app_path.read_text(encoding="utf-8")
    actions: list[str] = []
    if persistence_mode == "archive" and "StartupUri=" in text:
        # memory 仍使用 StartupUri；archive 须 Application_Startup 接收双击/命令行 {Ext}
        text = re.sub(
            r'\s*StartupUri="[^"]*"',
            '\n             Startup="Application_Startup"',
            text,
            count=1,
        )
        actions.append("patch App.xaml archive Startup handler")
    if is_empty_app_resources(app_path):
        text = re.sub(
            r"<Application\.Resources>.*?</Application\.Resources>",
            APP_RESOURCES_BLOCK.strip(),
            text,
            count=1,
            flags=re.DOTALL,
        )
        actions.append("patch App.xaml DefaultTheme merge")
    elif not actions:
        actions.append("App.xaml Resources not empty — skip theme inject")
    if not dry_run and actions:
        app_path.write_text(text, encoding="utf-8")
    return actions


def strip_dual_stack_csproj(text: str) -> str:
    pattern = re.compile(
        r"\n?\s*<!-- dual-stack:.*?-->(?:\s*\n\s*<ItemGroup>.*?</ItemGroup>)*",
        re.DOTALL,
    )
    while True:
        new_text = pattern.sub("\n", text, count=1)
        if new_text == text:
            break
        text = new_text
    text = re.sub(r"\n{3,}", "\n\n", text)
    if "</Project>" not in text:
        text = text.rstrip() + "\n\n</Project>\n"
    return text


def merge_csproj(csproj_path: Path, ctx: dict[str, str], dry_run: bool) -> list[str]:
    text = csproj_path.read_text(encoding="utf-8")
    actions: list[str] = []
    if "<!-- dual-stack:" in text:
        text = strip_dual_stack_csproj(text)
        actions.append("strip dual-stack blocks")
    snippets: list[str] = []
    abbr = ctx["Abbr"]
    mode = ctx["PersistenceMode"]

    def need(anchor: str) -> bool:
        return anchor not in text

    if need("dual-stack: packages"):
        snippets.append(CSPROJ_PACKAGES)
        actions.append("append packages")
    if need("dual-stack: resources"):
        snippets.append(CSPROJ_RESOURCES)
        actions.append("append resources")
    if need("dual-stack: properties"):
        snippets.append(CSPROJ_PROPERTIES)
        actions.append("append properties")
    anchor_py = f"dual-stack: {abbr}Py"
    if need(anchor_py):
        snippets.append(CSPROJ_PY_ITEM.format(abbr=abbr, py_folder=ctx["PyFolder"]))
        actions.append(f"append {ctx['PyFolder']}")
    anchor_env = f"dual-stack: {abbr}Env"
    if need(anchor_env):
        snippets.append(CSPROJ_ENV_ITEM.format(abbr=abbr, env_folder=ctx["EnvFolder"]))
        actions.append(f"append {ctx['EnvFolder']}")
    if mode == "archive" and need("dual-stack: baseline"):
        snippets.append(CSPROJ_BASELINE_ITEM)
        actions.append("append baseline")
    marker = f"dual-stack: persistence-{mode}"
    if need(marker):
        snippets.append(f"\n  <!-- {marker} -->\n")
        actions.append(f"mark persistence-{mode}")

    if snippets:
        insert = "\n".join(snippets) + "\n"
        text = text.replace("</Project>", insert + "</Project>")
        actions.append(f"patch {csproj_path.name}")
        if not dry_run:
            csproj_path.write_text(text, encoding="utf-8")
    else:
        actions.append("csproj already wired")
    return actions


def merge_gitignore(project_dir: Path, ctx: dict[str, str], dry_run: bool) -> list[str]:
    snippet_path = TEMPLATES / "gitignore-snippet.txt"
    snippet = substitute(snippet_path.read_text(encoding="utf-8"), ctx)
    gi = project_dir / ".gitignore"
    actions: list[str] = []
    if gi.is_file():
        existing = gi.read_text(encoding="utf-8")
        if ctx["EnvFolder"] + "/" in existing:
            return ["gitignore already contains Env"]
        if not dry_run:
            gi.write_text(existing.rstrip() + "\n\n" + snippet.strip() + "\n", encoding="utf-8")
        actions.append("append .gitignore")
    else:
        if not dry_run:
            gi.write_text(snippet.strip() + "\n", encoding="utf-8")
        actions.append("create .gitignore")
    return actions


def is_minimal_mainwindow(path: Path) -> bool:
    if not path.is_file():
        return True
    text = path.read_text(encoding="utf-8")
    return "Command=" not in text and len(text) < 900


PERSISTENCE_ALWAYS_REPLACE = frozenset(
    {
        "ApplicationBootstrap.cs",
        "CompositionRoot.cs",
        "CompositionRoot.ViewModels.cs",
        "MainWindow.xaml",
        "MainWindow.xaml.cs",
        "ViewModel/MainWindowViewModel.cs",
        "Services/ProjectSession.cs",
        "Model/Domain/SessionFormData.cs",
    }
)


def apply_writes(
    writes: list[tuple[Path, Path, str]],
    project_dir: Path,
    dry_run: bool,
    force_mainwindow: bool,
    force_docs: bool = False,
    force_persistence: bool = False,
) -> tuple[list[str], list[str]]:
    created: list[str] = []
    conflicts: list[str] = []
    mw_xaml = project_dir / "MainWindow.xaml"
    for _src, dest, content in writes:
        rel = dest.relative_to(project_dir).as_posix()
        if dest.exists():
            if force_persistence and rel.replace("\\", "/") in PERSISTENCE_ALWAYS_REPLACE:
                if not dry_run:
                    dest.write_text(content, encoding="utf-8")
                created.append(f"replace {rel}")
                continue
            if dest.name in ("MainWindow.xaml", "MainWindow.xaml.cs"):
                if force_mainwindow or is_minimal_mainwindow(mw_xaml):
                    if not dry_run:
                        dest.write_text(content, encoding="utf-8")
                    created.append(f"replace {rel}")
                else:
                    conflicts.append(rel)
                continue
            if force_docs and rel == "docs/开发说明.md":
                if not dry_run:
                    dest.write_text(content, encoding="utf-8")
                created.append(f"replace {rel}")
                continue
            try:
                if dest.read_text(encoding="utf-8") == content:
                    continue
            except OSError:
                pass
            if dest.name == PERSISTENCE_MARKER:
                if not dry_run:
                    dest.write_text(content, encoding="utf-8")
                created.append(f"update {rel}")
                continue
            conflicts.append(rel)
            continue
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
        created.append(rel)
    return created, conflicts


def remove_opposite_persistence(project_dir: Path, mode: str, dry_run: bool) -> list[str]:
    removed: list[str] = []
    opposite = "archive" if mode == "memory" else "memory"
    opp_root = TEMPLATES / "persistence" / opposite
    for src in iter_template_files(opp_root):
        rel = src.relative_to(opp_root)
        target = project_dir / rel
        if target.is_file():
            if not dry_run:
                target.unlink()
            removed.append(rel.as_posix())
    if mode == "memory":
        baseline = project_dir / "Assets"
        if baseline.is_dir():
            if not dry_run:
                shutil.rmtree(baseline, ignore_errors=True)
            removed.append("Assets/")
    return removed


def run_setup_python_env(project_dir: Path, abbr: str) -> int:
    """Create {Abbr}Env venv after scaffold (--apply default)."""
    script = SKILL_ROOT / "scripts" / "setup_python_env.py"
    cmd = [sys.executable, str(script), "--project-dir", str(project_dir), "--abbr", abbr]
    print("python-env:")
    print("+", " ".join(cmd))
    return subprocess.call(cmd)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--abbr", required=True)
    parser.add_argument("--root-namespace", required=True)
    parser.add_argument("--display-name", default="Application")
    parser.add_argument("--persistence", default="memory", choices=("memory", "archive"))
    parser.add_argument("--ext", default=".proj", help="Required for archive mode.")
    parser.add_argument("--app-id", default="", help="Required for memory mode (AppData folder).")
    parser.add_argument(
        "--include-form-demo",
        action="store_true",
        help="overlay SessionFormData + test form UI (memory 或 archive 夹具/E2E).",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force-mainwindow", action="store_true")
    parser.add_argument("--migrate-to", choices=("memory", "archive"), default="")
    parser.add_argument(
        "--skip-python-env",
        action="store_true",
        help="Do not run setup_python_env.py after --apply (default: auto-create venv).",
    )
    args = parser.parse_args()
    if not args.dry_run and not args.apply:
        print("Specify --dry-run or --apply", file=sys.stderr)
        sys.exit(2)

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.is_dir():
        raise SystemExit(f"Not a directory: {project_dir}")

    if args.migrate_to:
        args.persistence = args.migrate_to

    ctx = build_context(args)
    if has_non_ascii_path_part(ctx["PyFolder"]) or has_non_ascii_path_part(ctx["EnvFolder"]):
        raise SystemExit("Py/Env folder names must be ASCII.")

    if args.include_form_demo and ctx["PersistenceMode"] not in ("memory", "archive"):
        raise SystemExit("--include-form-demo requires --persistence memory or archive")

    dry_run = args.dry_run and not args.apply
    if args.migrate_to and not dry_run:
        remove_opposite_persistence(project_dir, ctx["PersistenceMode"], dry_run=False)

    writes = collect_template_writes(project_dir, ctx, include_form_demo=args.include_form_demo)
    created, conflicts = apply_writes(
        writes,
        project_dir,
        dry_run,
        args.force_mainwindow or args.apply,
        force_docs=bool(args.migrate_to),
        force_persistence=not dry_run and args.apply,
    )
    app_actions = patch_app_xaml(project_dir, dry_run, ctx["PersistenceMode"])
    csproj = find_csproj(project_dir)
    csproj_actions = merge_csproj(csproj, ctx, dry_run)
    gi_actions = merge_gitignore(project_dir, ctx, dry_run)

    print(f"mode={'dry-run' if dry_run else 'apply'}")
    print(f"persistence={ctx['PersistenceMode']}")
    print(f"formDemo={args.include_form_demo}")
    print(f"project={project_dir}")
    print("files:")
    for line in created:
        print(f"  + {line}")
    print("app.xaml:")
    for line in app_actions:
        print(f"  * {line}")
    print("csproj:")
    for line in csproj_actions:
        print(f"  * {line}")
    print("gitignore:")
    for line in gi_actions:
        print(f"  * {line}")
    if conflicts:
        print("CONFLICTS (not overwritten):")
        for c in conflicts:
            print(f"  ! {c}")
        if not dry_run:
            sys.exit(3)
    if not dry_run and args.apply and not args.skip_python_env:
        rc = run_setup_python_env(project_dir, ctx["Abbr"])
        if rc != 0:
            sys.exit(rc)
    print("OK")


if __name__ == "__main__":
    main()
