from __future__ import annotations

from pathlib import Path

from src.core.models import Document, Page
from src.ocr.adapters import TesseractOCRAdapter
from src.ocr.base import OCRConfig, OCRResult


class FakeExtractor:
    def __init__(self, result: OCRResult):
        self.result = result
        self.calls: list[Path] = []

    def extract_text(self, image_path: Path) -> OCRResult:
        self.calls.append(image_path)
        return self.result


def test_pdf_embedded_text_is_used(typed_pdf_fixture: Path, monkeypatch) -> None:
    doc = Document(source=typed_pdf_fixture, pages=[Page(index=1, source_path=typed_pdf_fixture)])
    extractor = FakeExtractor(OCRResult(text="from-ocr", confidence=0.2))
    adapter = TesseractOCRAdapter(extractor=extractor, config=OCRConfig())

    monkeypatch.setattr("src.ocr.adapters._extract_embedded_pdf_text", lambda _: ["Typed PDF fixture"])
    monkeypatch.setattr("src.ocr.adapters._rasterize_pdf_to_images", lambda *_: (_ for _ in ()).throw(RuntimeError("should not run")))

    output = adapter.extract(doc)
    assert output.pages[0].text == "Typed PDF fixture"
    assert output.pages[0].confidence == 1.0
    assert output.pages[0].metadata == {"source": "embedded-pdf-text"}
    assert extractor.calls == []


def test_pdf_scanned_falls_back_to_ocr(scanned_pdf_fixture: Path, screenshot_image_fixture: Path, monkeypatch) -> None:
    doc = Document(source=scanned_pdf_fixture, pages=[Page(index=1, source_path=scanned_pdf_fixture)])
    extractor = FakeExtractor(
        OCRResult(text="Recovered from OCR", confidence=0.87, metadata={"engine": "fake"}, error=None)
    )
    adapter = TesseractOCRAdapter(extractor=extractor, config=OCRConfig(dpi=400))

    monkeypatch.setattr("src.ocr.adapters._extract_embedded_pdf_text", lambda _: [""])
    monkeypatch.setattr("src.ocr.adapters._rasterize_pdf_to_images", lambda *_: [screenshot_image_fixture])

    output = adapter.extract(doc)
    assert output.pages[0].text == "Recovered from OCR"
    assert output.pages[0].confidence == 0.87
    assert output.pages[0].metadata == {"source": "ocr-rasterized-pdf", "engine": "fake"}
    assert extractor.calls == [screenshot_image_fixture]


def test_image_ocr_error_is_graceful(screenshot_image_fixture: Path) -> None:
    doc = Document(source=screenshot_image_fixture, pages=[Page(index=1, source_path=screenshot_image_fixture)])
    extractor = FakeExtractor(OCRResult(text="", confidence=None, metadata={"engine": "fake"}, error="Unreadable page"))
    adapter = TesseractOCRAdapter(extractor=extractor, config=OCRConfig(language="eng"))

    output = adapter.extract(doc)
    assert output.pages[0].error == "Unreadable page"
    assert output.pages[0].metadata == {"engine": "fake"}
