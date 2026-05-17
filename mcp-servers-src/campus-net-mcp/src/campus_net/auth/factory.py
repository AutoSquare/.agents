"""按 Profile.auth.type 分发认证后端；会话落盘仍在 ensure 模块。"""
from __future__ import annotations

import os

from campus_net.auth.base import AuthOutcome
from campus_net.auth.carsi import authenticate_carsi
from campus_net.auth.cas_vpn import authenticate_cas_vpn
from campus_net.auth.ip_only import authenticate_ip_only
from campus_net.profile.schema import CampusProfile


async def authenticate_unpersisted(
    profile: CampusProfile,
    *,
    harvest_doi: str | None = None,
) -> AuthOutcome | None:
    """
    调用与 auth.type 对应的适配器返回 AuthOutcome；
    credentials 仅从 Profile.credential_env 指向的环境变量读取。

    Returns:
        None 表示由上层 orchestrator 另行处理的情况（cas_vpn 缺少凭据、custom 类型等）。
    """
    sid = profile.school_id

    if profile.auth.type == "custom":
        return AuthOutcome(
            success=False,
            message="auth.type 为 custom：需改为 cas_vpn/ip_only 或扩展代码。",
            cookies=[],
        )

    if profile.auth.type == "ip_only":
        return await authenticate_ip_only(profile)

    if profile.auth.type == "carsi":
        return await authenticate_carsi(
            profile,
            _username_env=profile.credential_env.username,
            _password_env=profile.credential_env.password,
        )

    if profile.auth.type == "cas_vpn":
        from campus_net.auth.local_secrets import apply_local_secrets

        apply_local_secrets()
        u_env = profile.credential_env.username
        p_env = profile.credential_env.password
        username = os.environ.get(u_env, "").strip() or None
        password = os.environ.get(p_env, "").strip() or None
        if not username or not password:
            return AuthOutcome(
                success=False,
                message=(
                    f"环境变量缺失：请配置 {u_env} 与 {p_env}。"
                ),
                cookies=[],
            )
        return await authenticate_cas_vpn(
            profile,
            username=username,
            password=password,
            harvest_doi=harvest_doi,
        )

    return AuthOutcome(
        success=False,
        message=f"未知 auth.type（school_id={sid}）。",
        cookies=[],
    )
