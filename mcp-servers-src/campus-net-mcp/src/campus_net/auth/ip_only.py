"""仅靠 IP/VPN 出口，不显式表单登录。"""

from campus_net.auth.base import AuthOutcome
from campus_net.profile.schema import CampusProfile


async def authenticate_ip_only(profile: CampusProfile) -> AuthOutcome:
    """不发起浏览器登录。"""

    return AuthOutcome(
        success=True,
        message=(
            "auth.type 为 ip_only：假定已由校园 WiFi、客户端 VPN "
            "或系统代理接入校内出口；不进行表单登录。"
        ),
        cookies=[],
    )
