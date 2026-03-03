from __future__ import annotations

from datetime import datetime, timezone

from src.core.models import MarkdownRenderer, OCRDocument


class ObsidianMarkdownRenderer(MarkdownRenderer):
    def render(self, ocr_document: OCRDocument) -> str:
        created = datetime.now(timezone.utc).isoformat()
        lines = [
            "---",
            f"source: {ocr_document.source.name}",
            f"created: {created}",
            "tags:",
            "  - labnotescan",
            "---",
            "",
            f"# {ocr_document.source.stem}",
            "",
        ]
        for page_text in ocr_document.pages:
            lines.extend(
                [
                    f"## Page {page_text.page.index}",
                    "",
                    page_text.text,
                    "",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"
