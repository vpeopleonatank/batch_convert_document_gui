from __future__ import annotations

import subprocess
from pathlib import Path
from zipfile import ZipFile

import pytest

from src.core.convert import convert_doc_to_docx
from src.core.libreoffice import resolve_soffice_path


def _write_minimal_docx(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w") as zf:
        zf.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
""",
        )
        zf.writestr(
            "_rels/.rels",
            """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
""",
        )
        zf.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Hello</w:t></w:r></w:p>
  </w:body>
</w:document>
""",
        )


def test_convert_doc_to_docx_smoke(tmp_path: Path):
    soffice_path = resolve_soffice_path(None)
    if soffice_path is None:
        pytest.skip("LibreOffice `soffice` not available")

    source_docx = tmp_path / "source.docx"
    _write_minimal_docx(source_docx)

    result = subprocess.run(
        [
            str(soffice_path),
            "--headless",
            "--convert-to",
            "doc",
            "--outdir",
            str(tmp_path),
            str(source_docx),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip("LibreOffice cannot convert .docx → .doc in this environment")

    source_doc = tmp_path / "source.doc"
    if not source_doc.exists():
        pytest.skip("LibreOffice did not produce a .doc output")

    dest_dir = tmp_path / "out"
    success, _log = convert_doc_to_docx(soffice_path, source_doc, dest_dir)
    assert success
    assert (dest_dir / "source.docx").exists()

