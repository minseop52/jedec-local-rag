from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class PageAnalysis:
    primary_type: str
    content_tags: list[str]
    confidence: float
    reasons: list[str]
    routing: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


STRONG_FIGURE_CAPTION_RE = re.compile(
    r"^\s*Figure\s+\d+\s*[—\-–]\s+.+$",
    re.IGNORECASE | re.MULTILINE,
)

FIGURE_REFERENCE_RE = re.compile(
    r"\bFigure\s+\d+\b",
    re.IGNORECASE,
)

TABLE_CAPTION_RE = re.compile(
    r"^\s*Table\s+\d+\s*[—\-–]\s+.+$",
    re.IGNORECASE | re.MULTILINE,
)

TIMING_SIGNAL_RE = re.compile(
    r"\b(RESET_n|WRST_n|CK_t|CK_c|RDQS|WDQS|CATTRIP|AERR|DERR|R\[[0-9:]+\]|C\[[0-9:]+\])\b",
    re.IGNORECASE,
)

TIMING_TERM_RE = re.compile(
    r"\b(tINIT\d*|tPW_RESET|tWRSTL|tSLREP|T[a-zA-Z0-9]*)\b",
    re.IGNORECASE,
)

BUMP_MAP_LABEL_RE = re.compile(
    r"\b(VDDQ|VDDC|VSS|VPP|NC|No\s?Bump)\b",
    re.IGNORECASE,
)

WATERMARK_RE = re.compile(
    r"(Downloaded by|Chung-Ang University)",
    re.IGNORECASE,
)

HEADER_FOOTER_RE = re.compile(
    r"(JEDEC Standard No|Page\s+\d+)",
    re.IGNORECASE,
)

COORDINATE_RE = re.compile(r"[-+]?\d{3,5}")


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def analyze_page(
    text: str,
    table_count: int,
    table_row_counts: list[int],
) -> PageAnalysis:
    """
    Analyze a parsed PDF page.

    Important design decision:
    This function does NOT force a page into only one label such as
    normal_text/table_page/diagram_page.

    Instead, it returns:
    - primary_type: a rough dominant type
    - content_tags: multiple tags such as text, table, figure, timing_diagram
    - routing flags: whether to use text index, table index, image fallback, etc.
    """

    text = text or ""
    stripped_text = text.strip()
    text_length = len(stripped_text)

    content_tags: list[str] = []
    reasons: list[str] = []

    has_text = text_length > 0
    has_tables = table_count > 0

    has_strong_figure_caption = bool(STRONG_FIGURE_CAPTION_RE.search(text))
    figure_reference_count = len(FIGURE_REFERENCE_RE.findall(text))
    has_table_caption = bool(TABLE_CAPTION_RE.search(text))

    timing_signal_hits = len(TIMING_SIGNAL_RE.findall(text))
    timing_term_hits = len(TIMING_TERM_RE.findall(text))
    bump_map_hits = len(BUMP_MAP_LABEL_RE.findall(text))
    watermark_hits = len(WATERMARK_RE.findall(text))
    header_footer_hits = len(HEADER_FOOTER_RE.findall(text))
    coordinate_hits = len(COORDINATE_RE.findall(text))

    large_tables = sum(1 for rows in table_row_counts if rows >= 8)
    fragmented_tables = table_count >= 4 and large_tables <= 2

    if has_text:
        _append_unique(content_tags, "text")
        reasons.append(f"Extracted text detected: {text_length} characters")

    if has_tables:
        _append_unique(content_tags, "table")
        reasons.append(f"Extracted tables detected: {table_count}")

    if has_table_caption:
        _append_unique(content_tags, "table_caption")
        reasons.append("Standalone table caption detected")

    if has_strong_figure_caption:
        _append_unique(content_tags, "figure")
        _append_unique(content_tags, "figure_caption")
        reasons.append("Standalone figure caption detected")

    if figure_reference_count > 0 and not has_strong_figure_caption:
        _append_unique(content_tags, "figure_reference")
        reasons.append(f"Figure references in prose detected: {figure_reference_count}")

    if timing_signal_hits >= 3 or timing_term_hits >= 3:
        _append_unique(content_tags, "timing_diagram_or_timing_text")
        reasons.append(
            f"Timing-related signals/terms detected: signals={timing_signal_hits}, terms={timing_term_hits}"
        )

    if bump_map_hits >= 10:
        _append_unique(content_tags, "bump_map_or_layout")
        reasons.append(f"Bump-map/layout labels detected: {bump_map_hits}")

    if fragmented_tables:
        _append_unique(content_tags, "fragmented_tables")
        reasons.append("Extracted tables appear fragmented")

    if coordinate_hits >= 20:
        _append_unique(content_tags, "coordinate_heavy")
        reasons.append(f"Many coordinate-like numbers detected: {coordinate_hits}")

    if watermark_hits > 0:
        _append_unique(content_tags, "watermark_noise")
        reasons.append("Watermark noise detected")

    if header_footer_hits > 0:
        _append_unique(content_tags, "header_footer_noise")
        reasons.append("Header/footer text detected")

    # Page image should be stored for every page.
    image_available = True

    # Routing decisions
    use_text_index = has_text and text_length >= 100
    use_table_index = has_tables or has_table_caption

    requires_visual_context = (
        has_strong_figure_caption
        or "timing_diagram_or_timing_text" in content_tags
        or "bump_map_or_layout" in content_tags
        or "fragmented_tables" in content_tags
        or "coordinate_heavy" in content_tags
    )

    use_vision_fallback = requires_visual_context

    safe_for_text_chunking = use_text_index

    # Primary type is only a rough summary.
    if use_text_index and requires_visual_context:
        primary_type = "mixed"
        confidence = 0.85
    elif use_table_index and not use_text_index:
        primary_type = "table"
        confidence = 0.8
    elif use_table_index and use_text_index:
        primary_type = "mixed"
        confidence = 0.85
    elif use_text_index:
        primary_type = "text"
        confidence = 0.85
    elif requires_visual_context:
        primary_type = "visual"
        confidence = 0.75
    else:
        primary_type = "unknown"
        confidence = 0.0
        reasons.append("No strong content signal detected")

    routing = {
        "use_text_index": use_text_index,
        "use_table_index": use_table_index,
        "save_page_image": image_available,
        "requires_visual_context": requires_visual_context,
        "use_vision_fallback": use_vision_fallback,
        "safe_for_text_chunking": safe_for_text_chunking,
    }

    return PageAnalysis(
        primary_type=primary_type,
        content_tags=content_tags,
        confidence=confidence,
        reasons=reasons,
        routing=routing,
    )


# Backward-compatible name.
def classify_page(
    text: str,
    table_count: int,
    table_row_counts: list[int],
) -> PageAnalysis:
    return analyze_page(
        text=text,
        table_count=table_count,
        table_row_counts=table_row_counts,
    )