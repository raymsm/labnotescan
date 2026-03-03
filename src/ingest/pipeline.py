from __future__ import annotations

import mimetypes
import shutil
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from zipfile import ZipFile

from src.core.models import Document, Page

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | {".pdf", ".zip"}


class InputType(str, Enum):
    IMAGE = "image"
    PDF = "pdf"
    ZIP = "zip"


@dataclass
class IngestResult:
    documents: list[Document]
    temp_dir: tempfile.TemporaryDirectory[str] | None = None

    def cleanup(self) -> None:
        if self.temp_dir is not None:
            self.temp_dir.cleanup()
            self.temp_dir = None


def detect_input_type(path: Path) -> InputType:
    extension = path.suffix.lower()
    if extension in SUPPORTED_IMAGE_EXTENSIONS:
        return InputType.IMAGE
    if extension == ".pdf":
        return InputType.PDF
    if extension == ".zip":
        return InputType.ZIP

    mime, _ = mimetypes.guess_type(path.name)
    if mime and mime.startswith("image/"):
        return InputType.IMAGE
    if mime == "application/pdf":
        return InputType.PDF
    if mime == "application/zip":
        return InputType.ZIP

    raise ValueError(f"Unsupported input format: {path}")


def ingest_input(input_path: Path) -> IngestResult:
    if not input_path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")

    input_type = detect_input_type(input_path)
    if input_type in (InputType.IMAGE, InputType.PDF):
        return IngestResult(documents=[_document_from_file(input_path)])

    temp_dir = tempfile.TemporaryDirectory(prefix="labnotescan-")
    workspace = Path(temp_dir.name)
    extracted_files = _extract_zip_recursive(input_path, workspace)
    documents = [_document_from_file(p) for p in extracted_files]
    return IngestResult(documents=documents, temp_dir=temp_dir)


def _extract_zip_recursive(zip_path: Path, workspace: Path) -> list[Path]:
    destination = workspace / zip_path.stem
    destination.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path) as archive:
        archive.extractall(destination)

    normalized_files: list[Path] = []
    for child in sorted(destination.rglob("*")):
        if not child.is_file():
            continue
        try:
            child_type = detect_input_type(child)
        except ValueError:
            continue

        if child_type == InputType.ZIP:
            nested_workspace = workspace / f"nested-{child.stem}"
            nested_workspace.mkdir(parents=True, exist_ok=True)
            nested_zip = nested_workspace / child.name
            shutil.copy2(child, nested_zip)
            normalized_files.extend(_extract_zip_recursive(nested_zip, nested_workspace))
            continue

        normalized_files.append(child)

    return normalized_files


def _document_from_file(path: Path) -> Document:
    return Document(source=path, pages=[Page(index=1, source_path=path)])
