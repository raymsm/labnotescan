from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Page:
    index: int
    source_path: Path


@dataclass(frozen=True)
class Document:
    source: Path
    pages: list[Page]


@dataclass(frozen=True)
class OCRPageText:
    page: Page
    text: str


@dataclass(frozen=True)
class OCRDocument:
    source: Path
    pages: list[OCRPageText]


class OCRAdapter(Protocol):
    """Storage-independent OCR contract for `Document -> OCRDocument`."""

    def extract(self, document: Document) -> OCRDocument:
        ...


class MarkdownRenderer(Protocol):
    """Storage-independent renderer for `OCRDocument -> Markdown note`."""

    def render(self, ocr_document: OCRDocument) -> str:
        ...
