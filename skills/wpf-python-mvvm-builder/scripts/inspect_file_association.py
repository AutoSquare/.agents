# -*- coding: utf-8 -*-
"""Read-only inspect HKCU file association for archive {Ext} (Agent / maintainer diagnostic)."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

USER_CLASSES = r"Software\Classes"


def normalize_ext(ext: str) -> str:
    ext = ext.strip()
    if not ext.startswith("."):
        ext = "." + ext
    return ext


def read_registry_value(root_key, sub_path: str) -> str | None:
    try:
        import winreg
    except ImportError:
        return None
    try:
        with winreg.OpenKey(root_key, sub_path) as key:
            value, _ = winreg.QueryValueEx(key, "")
            return value if isinstance(value, str) else None
    except OSError:
        return None


def extract_quoted_exe(command: str | None) -> str | None:
    if not command:
        return None
    first = command.find('"')
    if first < 0:
        return None
    second = command.find('"', first + 1)
    if second < 0:
        return None
    return command[first + 1 : second]


def check_association(ext: str, prog_id: str, expected_exe: str | None) -> dict:
    ext = normalize_ext(ext)
    try:
        import winreg
    except ImportError:
        return {
            "ext": ext,
            "progId": prog_id,
            "status": "unsupported",
            "actionRequired": True,
            "agentPrompt": "非 Windows 或无法导入 winreg，跳过文件关联检查。",
        }

    ext_prog = read_registry_value(winreg.HKEY_CURRENT_USER, f"{USER_CLASSES}\\{ext}")
    icon_raw = read_registry_value(
        winreg.HKEY_CURRENT_USER, f"{USER_CLASSES}\\{prog_id}\\DefaultIcon"
    )
    open_cmd = read_registry_value(
        winreg.HKEY_CURRENT_USER, f"{USER_CLASSES}\\{prog_id}\\shell\\open\\command"
    )
    registered_exe = extract_quoted_exe(open_cmd)

    open_command_exe_match: bool | None = None
    if expected_exe and registered_exe:
        try:
            open_command_exe_match = (
                Path(expected_exe).resolve() == Path(registered_exe).resolve()
            )
        except OSError:
            open_command_exe_match = expected_exe.lower() == registered_exe.lower()

    issues: list[str] = []
    if ext_prog != prog_id:
        issues.append(f".ext ProgId mismatch: {ext_prog!r} != {prog_id!r}")
    if not open_cmd or "%1" not in open_cmd:
        issues.append("open command missing %1 placeholder")
    if not icon_raw:
        issues.append("DefaultIcon missing")
    if expected_exe and open_command_exe_match is False:
        issues.append("open command exe differs from expected")

    action_required = bool(issues) or not open_cmd
    status = "ok" if not action_required else "stale_or_missing"
    prompt = (
        "文件关联已同步。"
        if not action_required
        else f"关联需刷新：{'; '.join(issues) or '未注册'}。请 F5 运行一次应用以写入 HKCU。"
    )

    return {
        "ext": ext,
        "progId": prog_id,
        "extProgIdRegistered": ext_prog,
        "openCommand": open_cmd,
        "registeredExe": registered_exe,
        "expectedExe": expected_exe,
        "openCommandExeMatch": open_command_exe_match,
        "defaultIconPresent": bool(icon_raw),
        "status": status,
        "issues": issues,
        "actionRequired": action_required,
        "agentPrompt": prompt,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ext", required=True, help="e.g. .ast")
    parser.add_argument("--prog-id", required=True, help="e.g. AgentStatistics.ProjectFile")
    parser.add_argument(
        "--expected-exe",
        default="",
        help="Optional: compare open command to this exe (e.g. Debug AgentStatistics.exe)",
    )
    parser.add_argument("--check", action="store_true", help="Print JSON report to stdout")
    args = parser.parse_args()

    expected = args.expected_exe.strip() or None
    report = check_association(args.ext, args.prog_id.strip(), expected)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.check and report.get("actionRequired"):
        sys.exit(1)


if __name__ == "__main__":
    main()
