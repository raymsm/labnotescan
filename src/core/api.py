from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.core.pipeline import ConversionOutput, ConversionPipeline
from src.markdown.renderer import ObsidianMarkdownRenderer
from src.ocr.adapters import TesseractImageExtractor, TesseractOCRAdapter
from src.ocr.base import OCRConfig


@dataclass(frozen=True)
class ConversionOptions:
    """Stable cross-platform options for document conversion."""

    ocr_language: str = "eng"
    ocr_dpi: int = 300
    ocr_preprocessing: str = "none"


def build_default_pipeline(options: ConversionOptions) -> ConversionPipeline:
    ocr_config = OCRConfig(
        language=options.ocr_language,
        dpi=options.ocr_dpi,
        preprocessing=options.ocr_preprocessing,
    )
    extractor = TesseractImageExtractor(config=ocr_config)
    return ConversionPipeline(
        ocr_adapter=TesseractOCRAdapter(extractor=extractor, config=ocr_config),
        markdown_renderer=ObsidianMarkdownRenderer(),
    )


def convert(
    input_uri: str | Path,
    output_dir: str | Path,
    options: ConversionOptions | None = None,
    pipeline: ConversionPipeline | None = None,
) -> list[ConversionOutput]:
    """Stable API for CLI/mobile wrappers: `convert(input_uri, output_dir, options)`."""

    resolved_options = options or ConversionOptions()
    runner = pipeline or build_default_pipeline(resolved_options)
    return runner.convert(Path(input_uri), Path(output_dir))
