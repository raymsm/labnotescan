from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.core.models import MarkdownRenderer, OCRDocument, OCRPageText

_OBSIDIAN_FORBIDDEN_CHARS = r"[\[\]#\^|]"
_NON_SAFE_CHARS = r"[^a-z0-9._-]+"


@dataclass(frozen=True)
class RenderedNote:
    filename: str
    content: str


class ObsidianMarkdownRenderer(MarkdownRenderer):
    def __init__(
        self,
        *,
        use_wikilinks: bool = True,
        include_page_headings: bool = True,
        include_confidence_markers: bool = True,
        low_confidence_threshold: float = 0.6,
        attachments_dir_name: str = "attachments",
    ) -> None:
        self.use_wikilinks = use_wikilinks
        self.include_page_headings = include_page_headings
        self.include_confidence_markers = include_confidence_markers
        self.low_confidence_threshold = low_confidence_threshold
        self.attachments_dir_name = attachments_dir_name

    def render(self, ocr_document: OCRDocument) -> str:
        created = datetime.now(timezone.utc).isoformat()
        ocr_engine = _resolve_ocr_engine(ocr_document)
        lines = [
            "---",
            f"source: {ocr_document.source.name}",
            f"created: {created}",
            "tags:",
            "  - labnotescan",
            f"ocr_engine: {ocr_engine}",
            "---",
            "",
            f"# {ocr_document.source.stem}",
            "",
        ]

        multi_page = len(ocr_document.pages) > 1
        for page_text in ocr_document.pages:
            if self.include_page_headings and multi_page:
                lines.extend([f"## Page {page_text.page.index}", ""])

            if self._is_low_confidence(page_text):
                confidence_pct = int((page_text.confidence or 0.0) * 100)
                lines.extend([f"> ⚠️ Low OCR confidence ({confidence_pct}%)", ""])

            lines.extend([page_text.text, ""])

        return "\n".join(lines).rstrip() + "\n"

    def render_note(
        self,
        ocr_document: OCRDocument,
        *,
        output_dir: Path,
        used_filenames: set[str],
    ) -> RenderedNote:
        note_filename = self._build_safe_filename(ocr_document.source.stem, ".md", used_filenames)
        attachment_ref = self._copy_attachment(ocr_document.source, output_dir)

        markdown = self.render(ocr_document)
        if attachment_ref is not None:
            embed_line = self._attachment_link(attachment_ref)
            markdown = markdown.rstrip() + "\n\n" + embed_line + "\n"

        return RenderedNote(filename=note_filename, content=markdown)

    def _copy_attachment(self, source: Path, output_dir: Path) -> str | None:
        if not source.exists():
            return None

        attachments_dir = output_dir / self.attachments_dir_name
        attachments_dir.mkdir(parents=True, exist_ok=True)
        safe_name = self._build_safe_filename(source.stem, source.suffix.lower(), {p.name for p in attachments_dir.iterdir()})
        destination = attachments_dir / safe_name
        shutil.copy2(source, destination)
        return f"{self.attachments_dir_name}/{destination.name}"

    def _attachment_link(self, attachment_rel_path: str) -> str:
        if self.use_wikilinks:
            return f"![[{attachment_rel_path}]]"
        alt_text = Path(attachment_rel_path).name
        return f"![{alt_text}]({attachment_rel_path})"

    def _build_safe_filename(self, name: str, extension: str, existing_names: set[str]) -> str:
        base_slug = _slugify(name)
        candidate = f"{base_slug}{extension}"
        counter = 2
        while candidate in existing_names:
            candidate = f"{base_slug}-{counter}{extension}"
            counter += 1
        return candidate

    def _is_low_confidence(self, page_text: OCRPageText) -> bool:
        if not self.include_confidence_markers:
            return False
        if page_text.confidence is None:
            return False
        return page_text.confidence < self.low_confidence_threshold


def _slugify(text: str) -> str:
    cleaned = re.sub(_OBSIDIAN_FORBIDDEN_CHARS, " ", text.strip().lower())
    cleaned = re.sub(_NON_SAFE_CHARS, "-", cleaned)
    cleaned = cleaned.strip("._-")
    return cleaned or "note"


def _resolve_ocr_engine(ocr_document: OCRDocument) -> str:
    for page in ocr_document.pages:
        if page.metadata and isinstance(page.metadata.get("source"), str):
            return str(page.metadata["source"])
    return "unknown"
