# LabNoteScan

LabNoteScan is an **offline-first** OCR-to-Markdown converter for lab notes.
It provides a storage-independent ingestion pipeline and OCR adapter workflow that can process images, PDFs, and ZIP bundles into Obsidian-friendly Markdown.

## Features

- **CLI-first**: Simple command-line interface for batch processing.
- **Offline-only**: No network calls. All OCR and processing happen locally.
- **Recursive Ingestion**: Automatically extracts and processes images and PDFs from ZIP archives.
- **Smart PDF Handling**:
  - Extracts embedded text from searchable PDFs.
  - Automatically rasterizes and performs OCR on scanned PDFs.
- **Obsidian Ready**: Generates Markdown with YAML frontmatter, tags, and attachment linking.
- **Cross-Platform Core**: Python logic designed to be wrapped by mobile (Android/iOS) or desktop interfaces.

## Requirements

- **Python**: 3.10 or higher.
- **Tesseract OCR**: Must be installed on your system.
  - **Windows**: Install via [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
  - **macOS**: `brew install tesseract`
  - **Linux**: `sudo apt install tesseract-ocr`

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-repo/labnotescan.git
cd labnotescan
```

### 2. Install dependencies
It is recommended to use a virtual environment:

```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -e .
```

## Usage

### Basic conversion
Convert a single file or a ZIP archive to a target directory:

```bash
labnotescan convert ./my-notes.pdf --out ./obsidian-vault/notes
```

### Advanced OCR configuration
You can tune the OCR engine via flags or a config file:

```bash
labnotescan convert ./scan.jpg --out ./notes \
  --ocr-language eng+fra \
  --ocr-dpi 400 \
  --ocr-preprocessing threshold \
  --verbose
```

### Using a configuration file
Create a `config.yaml`:
```yaml
ocr_language: eng
ocr_dpi: 300
ocr_preprocessing: grayscale
```

Run with:
```bash
labnotescan convert ./bundle.zip --out ./notes --config ./config.yaml
```

## Technical Architecture

The project is split into several modular components:
- `src.ingest`: Recursive file detection and ZIP extraction.
- `src.ocr`: Abstractions for OCR engines (Tesseract implementation included).
- `src.markdown`: Obsidian-specific rendering logic.
- `src.core`: Orchestration pipeline and stable API surface.

## Development

### Running tests
Tests use `pytest` and mock the OCR engine to ensure they can run in any environment:

```bash
pytest
```

### Project Structure
```text
android/      # Minimal Android app skeleton (WorkManager + SAF)
docs/         # Architecture and flow documentation
src/
  cli/        # CLI entrypoint and argument parsing
  core/       # Stable API and conversion orchestrator
  ingest/     # Input detection and recursive ZIP ingestion
  markdown/   # Obsidian-friendly markdown rendering
  ocr/        # OCR abstraction and Tesseract implementation
tests/        # Comprehensive test suite
```

## License
Distributed under the MIT License. See `LICENSE` for more information.
