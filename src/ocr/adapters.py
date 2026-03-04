from __future__ import annotations

import tempfile
from pathlib import Path

from src.core.models import Document, OCRAdapter, OCRDocument, OCRPageText, Page
from src.ocr.base import OCRConfig, OCRExtractor, OCRResult


class PlaceholderOCRAdapter(OCRAdapter):
    """Deterministic offline OCR stub until a real engine is wired in."""

    def extract(self, document: Document) -> OCRDocument:
        page_text = [
            OCRPageText(
                page=page,
                text=_placeholder_text(page.source_path),
                confidence=0.0,
                metadata={"source": "placeholder"},
            )
            for page in document.pages
        ]
        return OCRDocument(source=document.source, pages=page_text)


class TesseractOCRAdapter(OCRAdapter):
    """Offline adapter with embedded PDF text extraction and OCR fallback."""

    def __init__(self, extractor: OCRExtractor, config: OCRConfig):
        self.extractor = extractor
        self.config = config

    def extract(self, document: Document) -> OCRDocument:
        if document.source.suffix.lower() == ".pdf":
            return self._extract_pdf(document)

        pages = [self._extract_page(page) for page in document.pages]
        return OCRDocument(source=document.source, pages=pages)

    def _extract_pdf(self, document: Document) -> OCRDocument:
        embedded_text = _extract_embedded_pdf_text(document.source)
        if embedded_text is not None and any(chunk.strip() for chunk in embedded_text):
            pages = [
                OCRPageText(
                    page=Page(index=idx, source_path=document.source),
                    text=text,
                    confidence=1.0,
                    metadata={"source": "embedded-pdf-text"},
                )
                for idx, text in enumerate(embedded_text, start=1)
            ]
            return OCRDocument(source=document.source, pages=pages)

        rasterized_pages = _rasterize_pdf_to_images(document.source, self.config.dpi)
        page_text: list[OCRPageText] = []
        for idx, image_path in enumerate(rasterized_pages, start=1):
            result = self.extractor.extract_text(image_path)
            page_text.append(
                OCRPageText(
                    page=Page(index=idx, source_path=document.source),
                    text=result.text,
                    confidence=result.confidence,
                    metadata={"source": "ocr-rasterized-pdf", **result.metadata},
                    error=result.error,
                )
            )
        return OCRDocument(source=document.source, pages=page_text)

    def _extract_page(self, page: Page) -> OCRPageText:
        result = self.extractor.extract_text(page.source_path)
        return OCRPageText(
            page=page,
            text=result.text,
            confidence=result.confidence,
            metadata=result.metadata,
            error=result.error,
        )


class TesseractImageExtractor(OCRExtractor):
    """Best-effort tesseract OCR extractor with graceful error handling."""

    def __init__(self, config: OCRConfig):
        self.config = config

    def extract_text(self, image_path: Path) -> OCRResult:
        try:
            from PIL import Image, ImageOps
        except ImportError:
            return OCRResult(text="", error="Pillow is not installed", metadata={"source": "tesseract"})

        try:
            import pytesseract
        except ImportError:
            return OCRResult(text="", error="pytesseract is not installed", metadata={"source": "tesseract"})

        try:
            with Image.open(image_path) as img:
                preprocessed = self._preprocess(img, ImageOps)
                data = pytesseract.image_to_data(
                    preprocessed,
                    lang=self.config.language,
                    output_type=pytesseract.Output.DICT,
                )
        except Exception as exc:  # noqa: BLE001
            return OCRResult(
                text="",
                error=f"Unable to OCR page {image_path.name}: {exc}",
                metadata={"source": "tesseract"},
            )

        tokens = [token.strip() for token in data.get("text", []) if token.strip()]
        conf_values = [int(v) for v in data.get("conf", []) if str(v).strip() not in {"", "-1"}]
        confidence = None
        if conf_values:
            confidence = sum(conf_values) / (len(conf_values) * 100)
        return OCRResult(
            text=" ".join(tokens),
            confidence=confidence,
            metadata={
                "source": "tesseract",
                "language": self.config.language,
                "dpi": self.config.dpi,
                "preprocessing": self.config.preprocessing,
            },
        )

    def _preprocess(self, image, image_ops):
        if self.config.preprocessing == "grayscale":
            return image_ops.grayscale(image)
        if self.config.preprocessing == "threshold":
            grayscale = image_ops.grayscale(image)
            return grayscale.point(lambda p: 255 if p > 140 else 0)
        return image


def _extract_embedded_pdf_text(pdf_path: Path) -> list[str] | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None

    reader = PdfReader(str(pdf_path))
    return [page.extract_text() or "" for page in reader.pages]


def _rasterize_pdf_to_images(pdf_path: Path, dpi: int) -> list[Path]:
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise RuntimeError("pypdfium2 is required for scanned PDF OCR fallback") from exc

    temp_dir = tempfile.mkdtemp(prefix="labnotescan-pdf-")
    rendered_paths: list[Path] = []
    pdf = pdfium.PdfDocument(str(pdf_path))
    scale = dpi / 72
    for idx, page in enumerate(pdf, start=1):
        pil_image = page.render(scale=scale).to_pil()
        out_path = Path(temp_dir) / f"page-{idx}.png"
        pil_image.save(out_path)
        rendered_paths.append(out_path)
    return rendered_paths


def _placeholder_text(source_path: Path) -> str:
    return f"[ocr-pending] Extracted text placeholder for: {source_path.name}"
