from __future__ import annotations

from src.cli.main import build_parser, _resolve_options


def test_cli_ocr_flags_override_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args([
        "convert",
        "input.png",
        "--out",
        "out",
        "--ocr-language",
        "deu",
        "--ocr-dpi",
        "450",
        "--ocr-preprocessing",
        "threshold",
    ])

    cfg = _resolve_options(args)
    assert cfg.ocr_language == "deu"
    assert cfg.ocr_dpi == 450
    assert cfg.ocr_preprocessing == "threshold"
