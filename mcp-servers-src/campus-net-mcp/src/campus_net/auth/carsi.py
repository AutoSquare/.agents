"""CARSI/Shibboleth 机构 federated 登录（占位实现）。"""

from campus_net.auth.base import AuthOutcome
from campus_net.profile.schema import CampusProfile


async def authenticate_carsi(
    _: CampusProfile,
    *,
    _username_env: str,
    _password_env: str,
) -> AuthOutcome:
    """本版本不包含可移植的 SAML 全流程自动化，提示使用浏览器兜底。"""

    return AuthOutcome(
        success=False,
        message=(
            "carsi 类型当前未实现自动化 SAML 断言获取；请将 auth.type 设为 cas_vpn，"
            "或使用 import_browser_cookies 导入已登录会话。"
        ),
        cookies=[],
    )
