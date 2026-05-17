"""PDF 版本粗检：识别带行号的投稿稿/预印本特征。"""

from __future__ import annotations

import re

_LINE_NUM_SUFFIX = re.compile(r"\s+\d{1,3}\s*$")
_MANUSCRIPT_MARKERS = re.compile(
    r"(preprint|submitted version|accepted manuscript|uncorrected proof|"
    r"author['\u2019]?s original|draft manuscript|in press\b)",
    re.I,
)


def is_likely_manuscript_pdf(text_sample: str) -> tuple[bool, str]:
    """
    根据首页文本判断是否像投稿稿（Elsevier/期刊排版前常见右侧行号）。

    Returns:
        (True, reason) 若疑似投稿稿；(False, "") 若像刊出排版。
    """
    if not text_sample or len(text_sample) < 200:
        return False, ""

    if _MANUSCRIPT_MARKERS.search(text_sample):
        return True, "manuscript_marker_in_text"

    lines = [ln.rstrip() for ln in text_sample.splitlines() if ln.strip()]
    if len(lines) < 15:
        return False, ""

    numbered = sum(1 for ln in lines[:40] if _LINE_NUM_SUFFIX.search(ln))
    if numbered >= max(8, int(len(lines[:40]) * 0.45)):
        return True, "line_number_margin_format"

    return False, ""


def inspect_pdf_bytes(data: bytes, *, max_pages: int = 2) -> tuple[bool, str]:
    """解析 PDF 前几页并执行 is_likely_manuscript_pdf。"""
    if not data.startswith(b"%PDF"):
        return False, ""

    try:
        import pypdf
        from io import BytesIO

        reader = pypdf.PdfReader(BytesIO(data))
        chunks: list[str] = []
        for i in range(min(max_pages, len(reader.pages))):
            chunks.append(reader.pages[i].extract_text() or "")
        return is_likely_manuscript_pdf("\n".join(chunks))
    except Exception:
        return False, ""
