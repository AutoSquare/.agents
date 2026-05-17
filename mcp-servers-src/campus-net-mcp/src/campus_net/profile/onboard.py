"""onboard 结果校验（缺失字段清单与警告）。"""
from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from campus_net.profile.schema import CampusProfile


def assess_profile_payload(data: dict[str, Any]) -> dict[str, Any]:
    """对 Agent 拼装后的草稿做结构与业务规则检查。"""

    try:
        prof = CampusProfile.model_validate(data)
    except ValidationError as e:
        return {
            "structurally_valid": False,
            "pydantic_error": str(e),
            "missing_fields": [],
            "warnings": [],
            "blocking_missing": [],
            "ready_to_save": False,
            "profile": None,
        }

    blocking: list[str] = []
    warns: list[str] = []

    if prof.auth.type == "carsi":
        blocking.append(
            "auth.type：carsi 当前版本不支持自动 SAML 登录；请改为 cas_vpn 或通过 import_browser_cookies 导入会话。",
        )

    if prof.auth.type == "cas_vpn":
        lu = prof.auth.login_url or ""
        if not lu.startswith("https://"):
            blocking.append("auth.login_url 必须是以 https:// 开头的网页 VPN或统一入口。")
        elif not prof.auth.steps:
            warns.append(
                "auth.steps 为空；请按实际登录页补齐 Playwright 步骤，可参考内置吉林大学模板。",
            )

    if not prof.library_probes:
        warns.append(
            "library_probes 为空时将难以判断校内 IP 是否放行；强烈建议填入图书馆主页或发现系统 HTTPS 接口。",
        )

    if prof.cnki.enabled and not (
        isinstance(prof.cnki.entry_url, str) and prof.cnki.entry_url.startswith("https://")
    ):
        blocking.append(
            "cnki.enabled=true 时必须提供 cnki.entry_url（HTTPS）；若暂不需要 CNKI，请设 cnki.enabled=false。",
        )

    ready = len(blocking) == 0
    merged_notes = blocking + warns

    return {
        "structurally_valid": True,
        "profile": prof.model_dump(mode="python"),
        "blocking_missing": blocking,
        "warnings": warns,
        "missing_fields": merged_notes,
        "ready_to_save": ready,
    }


def normalize_doi(doi: str | None) -> str | None:
    """去除 DOI 前缀空白与 https://doi.org/ 包装。"""

    if not doi or not doi.strip():
        return None
    return doi.strip().removeprefix("https://doi.org/").strip()
