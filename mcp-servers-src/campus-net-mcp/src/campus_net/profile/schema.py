"""YAML Profile 契约，供 Pydantic 校验与会话运行时解析。"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

AuthType = Literal["ip_only", "cas_vpn", "carsi", "custom"]


class ProbeStep(BaseModel):
    """Playwright 声明式步骤（cas_vpn 等）。"""

    model_config = ConfigDict(extra="forbid")

    action: Literal["goto", "click", "fill", "wait", "wait_for_url"]
    selector: str | None = None
    field: Literal["username", "password"] | None = Field(
        default=None,
        description="fill 时映射 credential_env.username / password",
    )
    url: str | None = None
    milliseconds: int | None = Field(default=None, ge=0)
    substring: str | None = Field(
        default=None, description="wait_for_url 时 URL 需包含的子串"
    )


class AuthConfig(BaseModel):
    """认证方式与登录表单配置。"""

    model_config = ConfigDict(extra="allow")

    type: AuthType
    login_url: str | None = None
    steps: list[ProbeStep] = Field(default_factory=list)
    success_url_contains: list[str] = Field(
        default_factory=list,
        description="登录成功后 URL 任一子串匹配即视为成功",
    )
    headless: bool | None = True

    @field_validator("login_url")
    @classmethod
    def require_https_if_set(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith("https://"):
            raise ValueError("login_url 须使用 HTTPS")
        return v


class CredentialEnv(BaseModel):
    """环境变量名称，不向日志输出具体值。"""

    username: str = Field(default="CAMPUS_USERNAME")
    password: str = Field(default="CAMPUS_PASSWORD")


class LibraryProbe(BaseModel):
    """HTTP 馆藏探针。"""

    model_config = ConfigDict(extra="forbid")

    name: str
    url: str
    method: Literal["GET", "HEAD"] = "GET"
    expect_status: list[int] = Field(default_factory=lambda: [200, 302, 301, 303, 307, 308])
    timeout_seconds: float = Field(default=12.0, ge=1.0, le=60.0)


class PublisherProbe(BaseModel):
    """对出版社页或 DOI 解析链的粗略检测。"""

    model_config = ConfigDict(extra="forbid")

    doi: str
    timeout_seconds: float = Field(default=20.0, ge=5.0, le=120.0)


class CnkiConfig(BaseModel):
    """知网机构入口检索配置。"""

    enabled: bool = False
    entry_url: str = ""
    search_by: list[str] = Field(default_factory=lambda: ["doi", "title", "url"])

    @field_validator("entry_url")
    @classmethod
    def https_entry(cls, v: str) -> str:
        if v and not v.startswith("https://"):
            raise ValueError("cnki.entry_url 须使用 HTTPS 或为空")
        return v


class CampusProfile(BaseModel):
    """学校在册 Profile 的根模型。"""

    model_config = ConfigDict(extra="forbid")

    school_id: str = Field(pattern=r"^[a-z0-9_-]{2,48}$")
    school_name: str
    aliases: list[str] = Field(default_factory=list)

    auth: AuthConfig = Field(default_factory=lambda: AuthConfig(type="ip_only"))
    credential_env: CredentialEnv = Field(default_factory=CredentialEnv)

    library_probes: list[LibraryProbe] = Field(default_factory=list)
    publisher_probe: PublisherProbe | None = None

    doi_resolver_template: str | None = Field(
        default=None,
        description="含 {doi} 占位符的 HTTPS 馆藏解析 URL",
    )
    cnki: CnkiConfig = Field(default_factory=CnkiConfig)
    publisher_cookie_seeds: list[str] = Field(
        default_factory=list,
        description="CAS 登录后用于采集出版商 Cookie 的 HTTPS 种子 URL",
    )

    access_modes: list[str] = Field(default_factory=list)
    session_ttl_hours: float = Field(default=6.0, ge=0.5, le=168.0)
    download_rate_limit_seconds: float = Field(default=3.0, ge=0.5, le=120.0)
    builtin: bool | None = Field(
        default=None, description="由加载器填入，YAML 可不写"
    )

    @field_validator(
        "doi_resolver_template",
        mode="before",
    )
    @classmethod
    def empty_resolver_to_none(cls, v: Any) -> Any:
        if v == "":
            return None
        return v

    def model_dump_yaml_safe(self) -> dict[str, Any]:
        """用于序列化写入用户磁盘。"""

        d = self.model_dump(mode="python", exclude_none=True)
        d.pop("builtin", None)
        return d
