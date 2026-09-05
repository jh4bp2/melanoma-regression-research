from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


PAGE_MARKER_RE = re.compile(r"^=== PAGE (\d+) ===\s*$", re.MULTILINE)
SECTION_ALIASES = {
    "title": "Title",
    "abstract": "Abstract",
    "case report": "Case Report",
    "case reports": "Case Report",
    "case presentation": "Case Presentation",
    "case presentations": "Case Presentation",
    "clinical course": "Clinical Course",
    "patient information": "Case Presentation",
    "results": "Results",
    "discussion": "Discussion",
    "conclusion": "Conclusion",
    "conclusions": "Conclusion",
    "references": "References",
}
CASE_SECTION_PRIORITY = {
    "Case Report": 0,
    "Case Presentation": 0,
    "Clinical Course": 0,
    "Results": 1,
    "Abstract": 2,
    "Title": 3,
    "Unknown": 4,
    "Discussion": 5,
    "Conclusion": 6,
    "References": 9,
}


@dataclass(frozen=True)
class TextChunk:
    paper_id: int
    page_start: int
    page_end: int
    section: str
    chunk_index: int
    text: str


def read_page_text(extracted_text_path: Path) -> dict[int, str]:
    content = extracted_text_path.read_text(encoding="utf-8")
    matches = list(PAGE_MARKER_RE.finditer(content))
    if not matches:
        raise ValueError("Extracted text has no page markers")
    pages: dict[int, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        pages[int(match.group(1))] = content[start:end].strip()
    return pages


def _heading_for_line(line: str) -> str | None:
    normalized = re.sub(r"[\d.\s:]+$", "", line.strip().casefold())
    if len(normalized) > 80:
        return None
    return SECTION_ALIASES.get(normalized)


def chunk_pages(
    paper_id: int,
    pages: dict[int, str],
    max_chars: int = 5000,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    current_section = "Unknown"
    chunk_index = 0

    for page_number, page_text in sorted(pages.items()):
        buffers: list[tuple[str, str]] = []
        active_section = current_section
        active_lines: list[str] = []

        for line in page_text.splitlines():
            heading = _heading_for_line(line)
            if heading:
                if active_lines:
                    buffers.append((active_section, "\n".join(active_lines).strip()))
                active_section = heading
                current_section = heading
                active_lines = []
            else:
                active_lines.append(line)
        if active_lines:
            buffers.append((active_section, "\n".join(active_lines).strip()))

        for section, block in buffers:
            if not block:
                continue
            for offset in range(0, len(block), max_chars):
                text = block[offset : offset + max_chars].strip()
                if text:
                    chunks.append(
                        TextChunk(
                            paper_id=paper_id,
                            page_start=page_number,
                            page_end=page_number,
                            section=section,
                            chunk_index=chunk_index,
                            text=text,
                        )
                    )
                    chunk_index += 1
    return chunks


def bounded_chunk_context(
    chunks: list[TextChunk],
    *,
    max_chars: int = 24000,
    case_priority: bool = True,
) -> str:
    ordered = (
        sorted(
            chunks,
            key=lambda chunk: (
                CASE_SECTION_PRIORITY.get(chunk.section, 7),
                chunk.chunk_index,
            ),
        )
        if case_priority
        else chunks
    )
    rendered: list[str] = []
    used = 0
    for chunk in ordered:
        header = (
            f"[[CHUNK {chunk.chunk_index} | PAGE {chunk.page_start}"
            f"-{chunk.page_end} | SECTION {chunk.section}]]\n"
        )
        item = header + chunk.text
        if rendered and used + len(item) > max_chars:
            break
        rendered.append(item)
        used += len(item)
    return "\n\n".join(rendered)
