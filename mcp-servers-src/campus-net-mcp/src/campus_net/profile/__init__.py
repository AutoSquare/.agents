"""Profile 加载、注册表与草稿发现。"""

from campus_net.profile.loader import load_builtin_profile, load_profile, merge_overrides
from campus_net.profile.registry import (
    get_active_school_id,
    list_profiles,
    read_active_record,
    set_active_school_id,
)

__all__ = [
    "get_active_school_id",
    "list_profiles",
    "load_builtin_profile",
    "load_profile",
    "merge_overrides",
    "read_active_record",
    "set_active_school_id",
]
