from __future__ import annotations

import argparse
from pathlib import Path

from src.core.pipeline import ConversionPipeline
from src.markdown.renderer import ObsidianMarkdownRenderer
from src.ocr.adapters import TesseractImageExtractor, TesseractOCRAdapter
from src.ocr.base import OCRConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="labnotescan", description="Offline OCR to Markdown converter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="Convert supported files to markdown")
    convert_parser.add_argument("input", type=Path, help="Input file: image, PDF, or ZIP")
    convert_parser.add_argument("--out", required=True, type=Path, help="Output directory")
    convert_parser.add_argument("--config", type=Path, help="Optional YAML config file")
    convert_parser.add_argument("--ocr-language", default=None, help="OCR language (default: eng)")
    convert_parser.add_argument("--ocr-dpi", default=None, type=int, help="Rasterization DPI for scanned PDFs")
    convert_parser.add_argument(
        "--ocr-preprocessing",
        default=None,
        choices=["none", "grayscale", "threshold"],
        help="Image preprocessing strategy",
    )

    return parser


def _load_config(config_path: Path | None) -> dict[str, object]:
    if config_path is None:
        return {}
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required when --config is used") from exc

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("Config file must contain a top-level mapping")
    return data


def _resolve_ocr_config(args: argparse.Namespace) -> OCRConfig:
    file_cfg = _load_config(args.config)
    language = args.ocr_language or file_cfg.get("ocr_language") or "eng"
    dpi = args.ocr_dpi or file_cfg.get("ocr_dpi") or 300
    preprocessing = args.ocr_preprocessing or file_cfg.get("ocr_preprocessing") or "none"
    return OCRConfig(language=str(language), dpi=int(dpi), preprocessing=str(preprocessing))


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "convert":
        ocr_config = _resolve_ocr_config(args)
        extractor = TesseractImageExtractor(config=ocr_config)
        pipeline = ConversionPipeline(
            ocr_adapter=TesseractOCRAdapter(extractor=extractor, config=ocr_config),
            markdown_renderer=ObsidianMarkdownRenderer(),
        )
        outputs = pipeline.convert(args.input, args.out)
        print(f"Converted {len(outputs)} document(s) into {args.out}")
        for output in outputs:
            print(f"- {output.source.name} -> {output.markdown_path.name}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
