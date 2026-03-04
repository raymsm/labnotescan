from __future__ import annotations

from pathlib import Path

from src.core.models import OCRDocument, OCRPageText, Page
from src.markdown.renderer import ObsidianMarkdownRenderer


def _normalize_created(markdown: str) -> str:
    lines = markdown.splitlines()
    return "\n".join("created: <TIMESTAMP>" if line.startswith("created: ") else line for line in lines)


def test_render_note_snapshot_with_page_headings_and_confidence(tmp_path: Path) -> None:
    source_pdf = tmp_path / "Report #1.pdf"
    source_pdf.write_bytes(b"%PDF-1.4")

    doc = OCRDocument(
        source=source_pdf,
        pages=[
            OCRPageText(
                page=Page(index=1, source_path=source_pdf),
                text="High confidence text.",
                confidence=0.9,
                metadata={"source": "tesseract"},
            ),
            OCRPageText(
                page=Page(index=2, source_path=source_pdf),
                text="Low confidence text.",
                confidence=0.2,
                metadata={"source": "tesseract"},
            ),
        ],
    )

    renderer = ObsidianMarkdownRenderer()
    note = renderer.render_note(doc, output_dir=tmp_path, used_filenames=set())

    assert note.filename == "report-1.md"
    assert (tmp_path / "attachments" / "report-1.pdf").exists()
    assert _normalize_created(note.content).strip() == """---
source: Report #1.pdf
created: <TIMESTAMP>
tags:
  - labnotescan
ocr_engine: tesseract
---

# Report #1

## Page 1

High confidence text.

## Page 2

> ⚠️ Low OCR confidence (20%)

Low confidence text.

![[attachments/report-1.pdf]]
""".strip()


def test_renderer_markdown_link_mode_and_collision_handling(tmp_path: Path) -> None:
    source_one = tmp_path / "sample.png"
    source_two = tmp_path / "nested" / "sample.png"
    source_two.parent.mkdir()
    source_one.write_bytes(b"img-1")
    source_two.write_bytes(b"img-2")

    renderer = ObsidianMarkdownRenderer(use_wikilinks=False)

    first = renderer.render_note(
        OCRDocument(
            source=source_one,
            pages=[OCRPageText(page=Page(index=1, source_path=source_one), text="A")],
        ),
        output_dir=tmp_path,
        used_filenames=set(),
    )
    second = renderer.render_note(
        OCRDocument(
            source=source_two,
            pages=[OCRPageText(page=Page(index=1, source_path=source_two), text="B")],
        ),
        output_dir=tmp_path,
        used_filenames={first.filename},
    )

    assert first.filename == "sample.md"
    assert second.filename == "sample-2.md"
    assert "![sample.png](attachments/sample.png)" in first.content
    assert "![sample-2.png](attachments/sample-2.png)" in second.content
