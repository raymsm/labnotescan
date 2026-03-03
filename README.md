# LabNoteScan

LabNoteScan is an **offline-first** OCR-to-Markdown converter for lab notes.
It currently provides a project skeleton, ingestion pipeline, and CLI for converting supported inputs into Obsidian-friendly Markdown notes.

## Features

- CLI command: `labnotescan convert <input> --out <dir>`
- Supported inputs:
  - Images: `.png`, `.jpg`, `.jpeg`, `.webp`
  - PDF: `.pdf`
  - ZIP archives containing images/PDFs (including nested ZIPs)
- Normalized conversion contract:
  - `Document -> Pages -> OCR text -> Markdown note`
- Obsidian-friendly Markdown output
- No network dependency in the conversion path

## Offline guarantee

LabNoteScan performs **no network calls** during ingestion, conversion, OCR adapter execution (current placeholder adapter), or Markdown generation.
All processing runs locally in temporary and output directories.

## Installation (editable)

```bash
python -m pip install -e .
```

## Usage

Convert a single image:

```bash
labnotescan convert ./samples/lab-note.png --out ./notes
```

Convert a PDF:

```bash
labnotescan convert ./samples/experiment.pdf --out ./notes
```

Convert a ZIP archive:

```bash
labnotescan convert ./samples/batch.zip --out ./notes
```

## Project structure

```text
src/
  cli/        # CLI entrypoint
  core/       # Storage-independent pipeline contracts + orchestrator
  ingest/     # Input detection and recursive ZIP ingestion
  ocr/        # OCR adapter interfaces/implementations
  markdown/   # Obsidian-friendly markdown rendering
tests/        # Unit/integration tests
```
