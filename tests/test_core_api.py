from __future__ import annotations

from pathlib import Path

from src.core.api import ConversionOptions, convert
from src.markdown.renderer import ObsidianMarkdownRenderer
from src.ocr.adapters import PlaceholderOCRAdapter
from src.core.pipeline import ConversionPipeline


def test_convert_stable_api_with_injected_pipeline(tmp_path: Path) -> None:
    source_image = tmp_path / "sample.png"
    source_image.write_bytes(b"img")

    out_dir = tmp_path / "out"
    pipeline = ConversionPipeline(ocr_adapter=PlaceholderOCRAdapter(), markdown_renderer=ObsidianMarkdownRenderer())

    outputs = convert(input_uri=str(source_image), output_dir=str(out_dir), options=ConversionOptions(), pipeline=pipeline)

    assert len(outputs) == 1
    assert outputs[0].markdown_path.exists()
