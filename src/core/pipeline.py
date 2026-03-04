from __future__ import annotations

from dataclasses import dataclass
import logging
import tempfile
from pathlib import Path

from src.core.models import MarkdownRenderer, OCRAdapter
from src.ingest.pipeline import IngestResult, ingest_input

logger = logging.getLogger(__name__)


@dataclass
class ConversionOutput:
    source: Path
    markdown_path: Path


class ConversionPipeline:
    """Storage-independent `Document -> OCR text -> Markdown note` orchestrator."""

    def __init__(self, ocr_adapter: OCRAdapter, markdown_renderer: MarkdownRenderer):
        self.ocr_adapter = ocr_adapter
        self.markdown_renderer = markdown_renderer

    def convert(self, input_path: Path, output_dir: Path) -> list[ConversionOutput]:
        logger.info(f"Starting conversion for: {input_path}")
        ingest_result = ingest_input(input_path)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            outputs: list[ConversionOutput] = []
            used_note_filenames: set[str] = set()
            for document in ingest_result.documents:
                logger.info(f"Processing document: {document.source}")
                ocr_document = self.ocr_adapter.extract(document)
                if hasattr(self.markdown_renderer, "render_note"):
                    rendered_note = self.markdown_renderer.render_note(
                        ocr_document,
                        output_dir=output_dir,
                        used_filenames=used_note_filenames,
                    )
                    markdown = rendered_note.content
                    markdown_path = output_dir / rendered_note.filename
                else:
                    markdown = self.markdown_renderer.render(ocr_document)
                    markdown_path = output_dir / f"{document.source.stem}.md"

                logger.info(f"Writing markdown to: {markdown_path}")
                markdown_path.write_text(markdown, encoding="utf-8")
                used_note_filenames.add(markdown_path.name)
                outputs.append(ConversionOutput(source=document.source, markdown_path=markdown_path))
            return outputs
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise
        finally:
            _safe_cleanup(ingest_result)


def _safe_cleanup(ingest_result: IngestResult) -> None:
    ingest_result.cleanup()
