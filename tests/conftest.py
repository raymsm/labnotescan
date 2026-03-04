from __future__ import annotations

import base64
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_TYPED_PDF_BYTES = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 18 Tf
72 72 Td
(Typed PDF fixture) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000063 00000 n 
0000000120 00000 n 
0000000246 00000 n 
0000000316 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
410
%%EOF
"""

_SCANNED_PDF_BYTES = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 300] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 32 >>
stream
0.9 g
0 0 300 300 re
f
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000063 00000 n 
0000000120 00000 n 
0000000224 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
306
%%EOF
"""

_1X1_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAukB9mM5jN8AAAAASUVORK5CYII="
)


@pytest.fixture
def typed_pdf_fixture(tmp_path: Path) -> Path:
    path = tmp_path / "typed.pdf"
    path.write_bytes(_TYPED_PDF_BYTES)
    return path


@pytest.fixture
def scanned_pdf_fixture(tmp_path: Path) -> Path:
    path = tmp_path / "scanned.pdf"
    path.write_bytes(_SCANNED_PDF_BYTES)
    return path


@pytest.fixture
def screenshot_image_fixture(tmp_path: Path) -> Path:
    path = tmp_path / "screenshot.png"
    path.write_bytes(_1X1_PNG)
    return path


@pytest.fixture
def mixed_zip_fixture(
    tmp_path: Path,
    typed_pdf_fixture: Path,
    scanned_pdf_fixture: Path,
    screenshot_image_fixture: Path,
) -> Path:
    archive = tmp_path / "mixed.zip"
    with ZipFile(archive, "w") as zf:
        zf.write(typed_pdf_fixture, arcname="docs/typed.pdf")
        zf.write(scanned_pdf_fixture, arcname="docs/scanned.pdf")
        zf.write(screenshot_image_fixture, arcname="images/screenshot.png")
    return archive
