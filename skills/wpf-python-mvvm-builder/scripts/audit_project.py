# -*- coding: utf-8 -*-
"""Audit a WPF project for dual-stack MVVM scaffold readiness."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MARKER = ".dual-stack-persistence.json"
EXPECTED_DIRS = ("ViewModel", "Services", "Model", "Themes", "Resources", "Properties")
CSPROJ_ANCHORS = (
    "dual-stack: packages",
    "dual-stack: resources",
    "dual-stack: properties",
    "dual-stack: persistence-memory",
    "dual-stack: persistence-archive",
)


def find_csproj(project_dir: Path) -> Path | None:
    projects = list(project_dir.glob("*.csproj"))
    if not projects:
        return None
    for p in projects:
        text = p.read_text(encoding="utf-8")
        if "<UseWPF>true</UseWPF>" in text or "<UseWPF>True</UseWPF>" in text:
            return p
    return projects[0]


def read_persistence_mode(project_dir: Path, csproj_text: str) -> str:
    marker = project_dir / MARKER
    if marker.is_file():
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
            return data.get("persistence", "unknown")
        except json.JSONDecodeError:
            pass
    if "dual-stack: persistence-memory" in csproj_text:
        return "memory"
    if "dual-stack: persistence-archive" in csproj_text:
        return "archive"
    return "none"


def is_minimal_mainwindow(xaml_path: Path) -> bool:
    if not xaml_path.is_file():
        return False
    text = xaml_path.read_text(encoding="utf-8")
    return "<Grid>" in text and "Command=" not in text and len(text) < 900


def app_has_default_theme(app_xaml: Path) -> bool:
    if not app_xaml.is_file():
        return False
    return "DefaultTheme.xaml" in app_xaml.read_text(encoding="utf-8")


def audit(project_dir: Path, abbr: str, expect: str = "") -> str:
    lines: list[str] = ["# Dual-Stack MVVM Audit", "", f"- project: `{project_dir}`", f"- abbr: `{abbr}`", ""]
    csproj = find_csproj(project_dir)
    if csproj is None:
        lines.append("## FAIL\n- No `.csproj` found.")
        return "\n".join(lines)

    text = csproj.read_text(encoding="utf-8")
    mode = read_persistence_mode(project_dir, text)
    lines.append(f"- csproj: `{csproj.name}`")
    lines.append(f"- persistence: **{mode}**")
    lines.append(f"- UseWPF: **{'yes' if '<UseWPF>true</UseWPF>' in text else 'check'}**")

    lines.append("\n## Shell")
    for name in ("Themes/DefaultTheme.xaml", "Resources/icons", "Properties/Settings.settings"):
        p = project_dir / Path(name.replace("/", "\\"))
        lines.append(f"- `{name}`: {'present' if p.exists() else 'missing'}")
    lines.append(f"- App.xaml DefaultTheme: **{app_has_default_theme(project_dir / 'App.xaml')}**")

    lines.append("\n## Directories")
    py_folder = f"{abbr}Py"
    env_folder = f"{abbr}Env"
    for name in (*EXPECTED_DIRS, py_folder):
        p = project_dir / name
        lines.append(f"- `{name}`: {'present' if p.exists() else 'missing'}")
    lines.append(f"- `{env_folder}`: {'present' if (project_dir / env_folder).exists() else 'missing'}")
    env_py = project_dir / env_folder / "Scripts" / "python.exe"
    if not env_py.is_file():
        env_py = project_dir / env_folder / "bin" / "python"
    lines.append(f"- `{env_folder}/python`: {'present' if env_py.is_file() else '**missing — run setup_python_env.py**'}")
    if mode == "archive":
        lines.append(f"- `Assets/Baseline`: {'present' if (project_dir / 'Assets' / 'Baseline').exists() else 'missing'}")

    lines.append("\n## csproj anchors")
    for anchor in CSPROJ_ANCHORS:
        lines.append(f"- `{anchor}`: {'present' if anchor in text else 'missing'}")

    lines.append("\n## Persistence modules")
    if mode == "memory":
        lines.append(f"- SessionSnapshotStore: {(project_dir / 'Services' / 'SessionSnapshotStore.cs').exists()}")
        lines.append(f"- ProjectVault: {(project_dir / 'Model' / 'Persistence' / 'ProjectVault.cs').exists()} (expect absent)")
        lines.append(f"- ProjectFileService: {(project_dir / 'Services' / 'ProjectFileService.cs').exists()} (expect absent)")
    elif mode == "archive":
        lines.append(f"- ProjectVault: {(project_dir / 'Model' / 'Persistence' / 'ProjectVault.cs').exists()}")
        lines.append(f"- ProjectFileService: {(project_dir / 'Services' / 'ProjectFileService.cs').exists()}")
        lines.append(f"- SessionSnapshotStore: {(project_dir / 'Services' / 'SessionSnapshotStore.cs').exists()} (expect absent)")

    lines.append("\n## Persistence wiring")
    bootstrap = project_dir / "ApplicationBootstrap.cs"
    mw_cs = project_dir / "MainWindow.xaml.cs"
    mw_xaml = project_dir / "MainWindow.xaml"
    lines.append(f"- ApplicationBootstrap: {'present' if bootstrap.exists() else 'missing'}")
    if mw_cs.is_file():
        mw_text = mw_cs.read_text(encoding="utf-8")
        lines.append(f"- MainWindow calls ApplicationBootstrap: **{'ApplicationBootstrap' in mw_text}**")
        lines.append(f"- MainWindow calls PersistOnExit: **{'PersistOnExit' in mw_text}**")
        lines.append(f"- MainWindow Loaded + BuildUiState: **{'Loaded' in mw_text and 'BuildUiState' in mw_text}**")
    if bootstrap.is_file():
        boot_text = bootstrap.read_text(encoding="utf-8")
        lines.append(f"- WindowPlacement load/save: **{'LoadWindowPlacement' in boot_text and 'SaveWindowPlacement' in boot_text}**")
    if mode == "memory":
        snap_store = project_dir / "Services" / "SessionSnapshotStore.cs"
        user_store = project_dir / "Services" / "UserSettingsStore.cs"
        if snap_store.is_file():
            snap_text = snap_store.read_text(encoding="utf-8")
            lines.append(f"- SessionSnapshotStore reads statusText: **{'statusText' in snap_text}**")
            uses_raw_only = (
                "GetRawText()" in snap_text
                and "ReadTablePayload" not in snap_text
                and "GetString()" not in snap_text
            )
            lines.append(f"- SessionSnapshotStore ReadTablePayload (not GetRawText-only): **{not uses_raw_only}**")
        if user_store.is_file():
            user_text = user_store.read_text(encoding="utf-8")
            lines.append(f"- UserSettingsStore WindowPlacement: **{'WindowPlacementSettings' in user_text}**")
        calc_svc = project_dir / "Services" / "SampleCalculationService.cs"
        if calc_svc.is_file():
            calc_text = calc_svc.read_text(encoding="utf-8")
            lines.append(f"- SampleCalculationService no SaveSnapshot: **{'SaveSnapshot' not in calc_text}**")
    if mode == "memory" and mw_xaml.is_file():
        xaml = mw_xaml.read_text(encoding="utf-8")
        lines.append(f"- No file menu (memory): **{'打开' not in xaml and '另存为' not in xaml}**")
        sess = project_dir / "Services" / "ProjectSession.cs"
        if sess.is_file():
            lines.append(f"- ProjectSession.EnsureInitialized: **{'EnsureInitialized' in sess.read_text(encoding='utf-8')}**")
        form_data = project_dir / "Model" / "Domain" / "SessionFormData.cs"
        marker = project_dir / MARKER
        form_demo = False
        if marker.is_file():
            try:
                form_demo = bool(json.loads(marker.read_text(encoding="utf-8")).get("formDemo"))
            except json.JSONDecodeError:
                pass
        if form_demo:
            lines.append(f"- formDemo SessionFormData: **{form_data.is_file()}**")
            vm_path = project_dir / "ViewModel" / "MainWindowViewModel.cs"
            if vm_path.is_file():
                vm_text = vm_path.read_text(encoding="utf-8")
                lines.append(f"- formDemo auto-save timer: **{'_formAutoSaveTimer' in vm_text}**")
                lines.append(f"- formDemo LoadFormFromSession: **{'LoadFormFromSession' in vm_text}**")
            mw_cs_text = mw_cs.read_text(encoding="utf-8") if mw_cs.is_file() else ""
            lines.append(f"- formDemo CommitTextBoxBindings: **{'CommitTextBoxBindings' in mw_cs_text}**")
    if mode == "archive" and mw_xaml.is_file():
        xaml = mw_xaml.read_text(encoding="utf-8")
        lines.append(f"- File menu Open/Save: **{'打开' in xaml and '保存' in xaml}**")
        lines.append(f"- Ctrl+S KeyBinding: **{'KeyBinding' in xaml and 'SaveProjectCommand' in xaml}**")
        grid_menu = (
            "Grid.RowDefinitions" in xaml
            and 'Menu Grid.Row="0"' in xaml
            and "DefaulMenuBackground" in xaml
            and not ('<DockPanel' in xaml and '<Menu DockPanel.Dock="Top"' in xaml)
        )
        lines.append(f"- MainWindow Grid menu layout: **{grid_menu}**")
        app_xaml = project_dir / "App.xaml"
        app_cs = project_dir / "App.xaml.cs"
        if app_xaml.is_file():
            app_text = app_xaml.read_text(encoding="utf-8")
            lines.append(f"- App Startup handler (no StartupUri): **{'Application_Startup' in app_text and 'StartupUri' not in app_text}**")
        if app_cs.is_file():
            app_cs_text = app_cs.read_text(encoding="utf-8")
            lines.append(f"- App parses startup project path: **{'TryGetStartupProjectFilePath' in app_cs_text}**")
        lines.append(f"- FileAssociationUtilities: **{(project_dir / 'Services' / 'FileAssociationUtilities.cs').is_file()}**")
        bootstrap = project_dir / "ApplicationBootstrap.cs"
        if bootstrap.is_file():
            boot = bootstrap.read_text(encoding="utf-8")
            lines.append(f"- ConfigureStartupProjectPath: **{'ConfigureStartupProjectPath' in boot}**")
        sess = project_dir / "Services" / "ProjectSession.cs"
        if sess.is_file():
            st = sess.read_text(encoding="utf-8")
            lines.append(f"- PersistOnExit non-empty: **{bool(st.strip()) and 'PersistOnExit' in st and 'ProjectFileService' in st}**")
        marker = project_dir / MARKER
        form_demo = False
        if marker.is_file():
            try:
                form_demo = bool(json.loads(marker.read_text(encoding="utf-8")).get("formDemo"))
            except json.JSONDecodeError:
                pass
        if form_demo:
            form_data = project_dir / "Model" / "Domain" / "SessionFormData.cs"
            lines.append(f"- formDemo SessionFormData: **{form_data.is_file()}**")
            vm_path = project_dir / "ViewModel" / "MainWindowViewModel.cs"
            if vm_path.is_file():
                vm_text = vm_path.read_text(encoding="utf-8")
                lines.append(f"- formDemo LoadFormFromSession: **{'LoadFormFromSession' in vm_text}**")
            mw_cs_text = mw_cs.read_text(encoding="utf-8") if mw_cs.is_file() else ""
            lines.append(f"- formDemo CommitTextBoxBindings: **{'CommitTextBoxBindings' in mw_cs_text}**")

    lines.append("\n## MVVM hints")
    mw = project_dir / "MainWindow.xaml"
    lines.append(f"- MainWindow minimal (safe replace): **{is_minimal_mainwindow(mw)}**")
    lines.append(f"- CompositionRoot: {'present' if (project_dir / 'CompositionRoot.cs').exists() else 'missing'}")

    if expect and mode != expect:
        lines.append(f"\n## WARN")
        lines.append(f"- fixture expects persistence **{expect}**, actual **{mode}**")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--abbr", required=True)
    parser.add_argument(
        "--expect",
        choices=("memory", "archive"),
        default="",
        help="Warn if project persistence mode differs (memory or archive fixture).",
    )
    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()
    if not project_dir.is_dir():
        print(f"Not a directory: {project_dir}", file=sys.stderr)
        sys.exit(1)
    print(audit(project_dir, args.abbr.strip(), expect=args.expect.strip()))


if __name__ == "__main__":
    main()
