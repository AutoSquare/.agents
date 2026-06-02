# -*- coding: utf-8 -*-
"""Shared session_snapshot.json table payload read/migrate (mirrors C# SessionSnapshotStore)."""
from __future__ import annotations

import json
from typing import Any

CURRENT_SNAPSHOT_FORMAT_VERSION = 1
FORM_DEMO_TABLE = "测试表单"
FORM_DEMO_FIELDS = (
    "projectName",
    "ownerName",
    "memo",
    "contactPhone",
    "department",
    "siteAddress",
)


def unwrap_over_quoted_json(payload: str, max_layers: int = 4) -> str:
    current = payload
    for _ in range(max_layers):
        if len(current) < 2 or current[0] != '"' or current[-1] != '"':
            break
        try:
            inner = json.loads(current)
        except json.JSONDecodeError:
            break
        if not isinstance(inner, str) or inner == current:
            break
        current = inner
    return current


def read_table_payload(element: Any) -> str:
    """Read one dataTables/materialTables entry like C# ReadTablePayload."""
    if isinstance(element, str):
        payload = element
    elif isinstance(element, (dict, list)):
        payload = json.dumps(element, ensure_ascii=False)
    else:
        payload = json.dumps(element, ensure_ascii=False)
    return unwrap_over_quoted_json(payload)


def load_snapshot_tables(snapshot: dict) -> tuple[dict[str, str], dict[str, str]]:
    data_tables: dict[str, str] = {}
    material_tables: dict[str, str] = {}
    for name, raw in snapshot.get("dataTables", {}).items():
        if isinstance(raw, str):
            data_tables[name] = unwrap_over_quoted_json(raw)
        else:
            data_tables[name] = read_table_payload(raw)
    for name, raw in snapshot.get("materialTables", {}).items():
        if isinstance(raw, str):
            material_tables[name] = unwrap_over_quoted_json(raw)
        else:
            material_tables[name] = read_table_payload(raw)
    return data_tables, material_tables


def table_json_parseable(payload: str) -> bool:
    if not payload.strip():
        return True
    try:
        json.loads(payload)
        return True
    except json.JSONDecodeError:
        return False


def looks_legacy_or_corrupt(snapshot: dict) -> list[str]:
    """Return human-readable issues; empty if snapshot tables look loadable."""
    issues: list[str] = []
    version = snapshot.get("formatVersion")
    if version is None:
        issues.append("missing formatVersion")
    elif version != CURRENT_SNAPSHOT_FORMAT_VERSION:
        issues.append(f"formatVersion={version} (current={CURRENT_SNAPSHOT_FORMAT_VERSION})")

    for section in ("dataTables", "materialTables"):
        tables = snapshot.get(section, {})
        if not isinstance(tables, dict):
            issues.append(f"{section} is not an object")
            continue
        for name, raw in tables.items():
            if isinstance(raw, str) and raw.startswith('"') and raw.endswith('"'):
                issues.append(f"{section}.{name}: wrapped JSON string (GetRawText legacy load)")
            payload = read_table_payload(raw) if not isinstance(raw, str) else unwrap_over_quoted_json(raw)
            if not table_json_parseable(payload):
                issues.append(f"{section}.{name}: not valid JSON after normalize")

    return issues


def parse_form_demo(payload: str) -> dict[str, str] | None:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return {key: str(data.get(key, "") or "") for key in FORM_DEMO_FIELDS}


def migrate_snapshot_dict(snapshot: dict, display_name: str = "") -> dict:
    """Normalize tables to current memory on-disk shape."""
    data_tables, material_tables = load_snapshot_tables(snapshot)
    ui_state = snapshot.get("uiState")
    if not isinstance(ui_state, dict):
        ui_state = {}
    return {
        "formatVersion": CURRENT_SNAPSHOT_FORMAT_VERSION,
        "displayName": snapshot.get("displayName") or display_name or "Application",
        "dataTables": data_tables,
        "materialTables": material_tables,
        "uiState": ui_state,
    }
