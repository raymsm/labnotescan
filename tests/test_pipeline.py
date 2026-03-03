from __future__ import annotations

from pathlib import Path

from src.core.pipeline import ConversionPipeline
from src.markdown.renderer import ObsidianMarkdownRenderer
from src.ocr.adapters import PlaceholderOCRAdapter


def test_conversion_pipeline_writes_markdown(tmp_path: Path) -> None:
    source_image = tmp_path / "sample.png"
    source_image.write_bytes(b"img")

    out_dir = tmp_path / "out"

    pipeline = ConversionPipeline(
        ocr_adapter=PlaceholderOCRAdapter(),
        markdown_renderer=ObsidianMarkdownRenderer(),
    )

    outputs = pipeline.convert(source_image, out_dir)
    assert len(outputs) == 1

    markdown_file = out_dir / "sample.md"
    assert markdown_file.exists()
    content = markdown_file.read_text(encoding="utf-8")
    assert "# sample" in content
    assert "[ocr-pending]" in content
