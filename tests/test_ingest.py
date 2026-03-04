from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

from src.ingest.pipeline import InputType, detect_input_type, ingest_input


def test_detect_input_type_image() -> None:
    assert detect_input_type(Path("note.png")) == InputType.IMAGE


def test_detect_input_type_pdf() -> None:
    assert detect_input_type(Path("note.pdf")) == InputType.PDF


def test_ingest_nested_zip(tmp_path: Path) -> None:
    inner_img = tmp_path / "inner.jpg"
    inner_img.write_bytes(b"fake image bytes")

    inner_zip = tmp_path / "inner.zip"
    with ZipFile(inner_zip, "w") as zf:
        zf.write(inner_img, arcname="inner.jpg")

    outer_pdf = tmp_path / "outer.pdf"
    outer_pdf.write_bytes(b"%PDF-1.4")

    outer_zip = tmp_path / "outer.zip"
    with ZipFile(outer_zip, "w") as zf:
        zf.write(inner_zip, arcname="nested/inner.zip")
        zf.write(outer_pdf, arcname="outer.pdf")

    result = ingest_input(outer_zip)
    try:
        names = sorted(doc.source.name for doc in result.documents)
        assert names == ["inner.jpg", "outer.pdf"]
        assert all(doc.pages[0].index == 1 for doc in result.documents)
    finally:
        result.cleanup()


def test_ingest_mixed_zip_fixture(mixed_zip_fixture: Path) -> None:
    result = ingest_input(mixed_zip_fixture)
    try:
        names = sorted(doc.source.name for doc in result.documents)
        assert names == ["scanned.pdf", "screenshot.png", "typed.pdf"]
    finally:
        result.cleanup()
