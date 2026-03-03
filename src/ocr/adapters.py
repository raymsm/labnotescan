from __future__ import annotations

from pathlib import Path

from src.core.models import Document, OCRAdapter, OCRDocument, OCRPageText


class PlaceholderOCRAdapter(OCRAdapter):
    """Deterministic offline OCR stub until a real engine is wired in."""

    def extract(self, document: Document) -> OCRDocument:
        page_text = [
            OCRPageText(
                page=page,
                text=_placeholder_text(page.source_path),
            )
            for page in document.pages
        ]
        return OCRDocument(source=document.source, pages=page_text)


def _placeholder_text(source_path: Path) -> str:
    return f"[ocr-pending] Extracted text placeholder for: {source_path.name}"
