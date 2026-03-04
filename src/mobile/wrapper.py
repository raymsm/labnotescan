from __future__ import annotations

from pathlib import Path

from src.core.api import ConversionOptions, convert as core_convert
from src.core.pipeline import ConversionOutput


def convert(input_uri: str, output_dir: str, options: ConversionOptions | None = None) -> list[ConversionOutput]:
    """Mobile-friendly wrapper that forwards to the stable core API."""

    return core_convert(input_uri=Path(input_uri), output_dir=Path(output_dir), options=options)
