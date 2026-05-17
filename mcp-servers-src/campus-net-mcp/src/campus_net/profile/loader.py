"""从内建与用户目录加载并解析 CampusProfile。"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from pydantic import ValidationError

from campus_net.profile.paths import bundled_profiles_dir, user_profiles_dir
from campus_net.profile.schema import CampusProfile


def builtin_index_path() -> Path:
    return bundled_profiles_dir() / "builtin" / "index.yaml"


def builtin_profile_path(school_id: str) -> Path:
    return bundled_profiles_dir() / "builtin" / f"{school_id}.yaml"


def _read_yaml(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"无效的 YAML 根类型: {path}")
    return data


def resolve_alias(alias: str) -> str | None:
    """将中文或简称解析为 school_id。"""

    index_path = builtin_index_path()
    if not index_path.is_file():
        return None
    data = _read_yaml(index_path)
    aliases = data.get("aliases") or {}
    if not isinstance(aliases, dict):
        return None
    key = alias.strip().lower()
    for canon, variants in aliases.items():
        canon_l = canon.lower()
        if key == canon_l:
            return canon
        if isinstance(variants, list):
            for v in variants:
                if isinstance(v, str) and key == v.strip().lower():
                    return canon
    return None


def load_yaml_dict(path: Path) -> dict:
    """加载 YAML 字典。"""

    return _read_yaml(path)


def load_builtin_profile(school_id: str) -> CampusProfile:
    """加载内置 Profile。"""

    path = builtin_profile_path(school_id)
    if not path.is_file():
        raise FileNotFoundError(school_id)
    data = _read_yaml(path)
    data.setdefault("school_id", school_id)
    data["builtin"] = True
    return CampusProfile.model_validate(data)


def load_user_profile(school_id: str) -> CampusProfile:
    """加载用户目录 ~/.cursor/campus-net/profiles/{school_id}.yaml"""

    path = user_profiles_dir() / f"{school_id}.yaml"
    if not path.is_file():
        raise FileNotFoundError(str(path))
    data = _read_yaml(path)
    data.setdefault("school_id", school_id)
    data["builtin"] = False
    return CampusProfile.model_validate(data)


def save_user_profile_yaml(profile: CampusProfile, overwrite: bool = True) -> Path:
    """将 Profile 写入用户目录。"""

    path = user_profiles_dir() / f"{profile.school_id}.yaml"
    if path.exists() and not overwrite:
        raise FileExistsError(str(path))
    dump = profile.model_dump_yaml_safe()
    text = yaml.safe_dump(dump, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(text, encoding="utf-8")
    return path


def load_profile(school_id: str) -> CampusProfile:
    """用户 Profile 优先，否则退回 builtin。"""

    try:
        return load_user_profile(school_id)
    except FileNotFoundError:
        return load_builtin_profile(school_id)


def merge_overrides(profile: CampusProfile, patch: dict) -> CampusProfile:
    """合并 Agent 传来的局部字段后重新校验（用于 onboard）。"""

    base = profile.model_dump(mode="python")
    _deep_merge_dict(base, patch)
    return CampusProfile.model_validate(base)


def _deep_merge_dict(a: dict, b: dict) -> None:
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(a.get(k), dict):
            _deep_merge_dict(a[k], v)  # type: ignore[index]
        else:
            a[k] = v


def validate_profile_yaml_text(yaml_text: str) -> tuple[CampusProfile | None, str | None]:
    """校验 YAML 文本，返回 Profile 或错误信息。"""

    try:
        data = yaml.safe_load(yaml_text)
        if not isinstance(data, dict):
            return None, "根节点须为 YAML 映射"
        return CampusProfile.model_validate(data), None
    except (yaml.YAMLError, ValidationError, ValueError) as e:
        return None, str(e)
