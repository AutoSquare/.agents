"""从 HTML 落地页解析 PDF 直链。"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse


_PDF_HREF = re.compile(r"""href=["']([^"']+\.pdf[^"']*)["']""", re.I)
_META_PDF = re.compile(
    r"""(?:citation_pdf_url|pdf_url|og:pdf)["']\s+content=["']([^"']+)["']""",
    re.I,
)
_PDFFT = re.compile(r"""href=["']([^"']*pdfft[^"']*)["']""", re.I)
_LINKINGHUB_REDIRECT = re.compile(
    r'Redirect=([^"\'\s&]+)|redirectURL"\s+value="([^"]+)"',
    re.I,
)


def extract_pdf_links_from_html(html: str, base_url: str) -> list[str]:
    """从 HTML 中抽取可能的 PDF 下载链接。"""
    found: list[str] = []
    for pattern in (_META_PDF, _PDFFT, _PDF_HREF):
        for m in pattern.finditer(html):
            raw = m.group(1).strip()
            if not raw:
                continue
            u = urljoin(base_url, raw)
            if u.startswith("https://") and u not in found:
                found.append(u)

    host = (urlparse(base_url).hostname or "").lower()
    if "linkinghub.elsevier.com" in host:
        for m in _LINKINGHUB_REDIRECT.finditer(html):
            enc = m.group(1) or m.group(2)
            if not enc:
                continue
            from urllib.parse import unquote

            target = unquote(enc)
            if target.startswith("https://") and target not in found:
                found.append(target)
            perm = (
                "https://linkinghub.elsevier.com/retrieve/articleSelectSinglePerm"
                f"?Redirect={enc}&key="
            )
            key_m = re.search(r'name="key"\s+value="([^"]+)"', html)
            if key_m:
                perm = perm + key_m.group(1)
                if perm not in found:
                    found.append(perm)

    return found


def merge_unique_candidates(*groups: list[str]) -> list[str]:
    """按顺序去重合并候选 URL。"""
    out: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for u in group:
            if not isinstance(u, str) or not u.startswith("https://"):
                continue
            if u in seen:
                continue
            seen.add(u)
            out.append(u)
    return out
