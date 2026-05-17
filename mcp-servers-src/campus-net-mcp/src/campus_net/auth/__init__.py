"""校园网馆藏认证适配器。"""

from campus_net.auth.base import AuthOutcome
from campus_net.auth.ensure import attempt_authentication
from campus_net.auth.factory import authenticate_unpersisted

__all__ = ["AuthOutcome", "authenticate_unpersisted", "attempt_authentication"]
