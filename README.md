# LabNoteScan

LabNoteScan is an **offline-first** OCR-to-Markdown converter for lab notes.
It provides a storage-independent ingestion pipeline and OCR adapter workflow that can process images, PDFs, and ZIP bundles into Obsidian-friendly Markdown.

## Features

- CLI command: `labnotescan convert <input> --out <dir>`
- Supported inputs:
  - Images: `.png`, `.jpg`, `.jpeg`, `.webp`
  - PDF: `.pdf`
  - ZIP archives containing images/PDFs (including nested ZIPs)
- OCR pipeline with:
  - Embedded PDF text extraction when present
  - Rasterization + OCR fallback for scanned PDFs
  - OCR language / DPI / preprocessing configuration
- Normalized conversion contract:
  - `Document -> Pages -> OCR text -> Markdown note`
- Obsidian-friendly Markdown output
- Stable core API for wrappers:
  - `convert(input_uri, output_dir, options)`
- No network dependency in the conversion path

## OCR configuration

Set OCR options via CLI flags:

```bash
labnotescan convert ./samples/scan.pdf --out ./notes \
  --ocr-language eng \
  --ocr-dpi 300 \
  --ocr-preprocessing grayscale
```

Or pass a YAML file:

```yaml
ocr_language: eng
ocr_dpi: 300
ocr_preprocessing: threshold
```

```bash
labnotescan convert ./samples/scan.pdf --out ./notes --config ./config.yaml
```

## Offline guarantee

LabNoteScan performs **no network calls** during ingestion, conversion, OCR adapter execution, or Markdown generation.
All processing runs locally in temporary and output directories.

## Installation (editable)

```bash
python -m pip install -e .
```

## Project structure

```text
src/
  cli/        # CLI entrypoint
  core/       # Storage-independent pipeline contracts + orchestrator
  ingest/     # Input detection and recursive ZIP ingestion
  ocr/        # OCR abstraction and offline implementations
  markdown/   # Obsidian-friendly markdown rendering
tests/        # Unit/integration tests
```

## Mobile wrapper contract

Shared API surface for CLI/mobile wrappers:

```python
from src.core.api import ConversionOptions, convert

outputs = convert(
    input_uri="/path/to/input.pdf",
    output_dir="/path/to/output",
    options=ConversionOptions(ocr_language="eng", ocr_dpi=300, ocr_preprocessing="none"),
)
```

See Android planning and flow docs:
- `docs/android.md`
- `docs/e2e-obsidian-flow.md`
