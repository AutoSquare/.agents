# campus-net-mcp

通用 Profile 驱动的校园网与馆藏 MCP 服务。开发与配置说明请见：[校园网 MCP 开发文档](../../docs/校园网MCP开发文档.md)。

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
playwright install chromium
python server.py
```

## 配置

在用户目录 `%USERPROFILE%\.cursor\campus-net\` 下写入激活学校与自建 Profile。

环境变量（默认）：`CAMPUS_USERNAME`、`CAMPUS_PASSWORD`；可选用 `OPENALEX_EMAIL` 作为 Unpaywall 礼貌池邮箱（与 academic-research 一致时可复用）。
