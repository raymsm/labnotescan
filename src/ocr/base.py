from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class OCRResult:
    text: str
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class OCRExtractor(Protocol):
    """Per-image OCR abstraction for offline extractors."""

    def extract_text(self, image_path: Path) -> OCRResult:
        ...


@dataclass(frozen=True)
class OCRConfig:
    language: str = "eng"
    dpi: int = 300
    preprocessing: str = "none"
