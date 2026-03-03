from __future__ import annotations

import argparse
from pathlib import Path

from src.core.pipeline import ConversionPipeline
from src.markdown.renderer import ObsidianMarkdownRenderer
from src.ocr.adapters import PlaceholderOCRAdapter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="labnotescan", description="Offline OCR to Markdown converter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="Convert supported files to markdown")
    convert_parser.add_argument("input", type=Path, help="Input file: image, PDF, or ZIP")
    convert_parser.add_argument("--out", required=True, type=Path, help="Output directory")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "convert":
        pipeline = ConversionPipeline(
            ocr_adapter=PlaceholderOCRAdapter(),
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
