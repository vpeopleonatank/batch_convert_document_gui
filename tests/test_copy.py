from __future__ import annotations

from pathlib import Path

from src.core.copy import copy_docx


def test_copy_docx_copies_content(tmp_path: Path):
    source = tmp_path / "in.docx"
    source.write_bytes(b"hello")

    dest = tmp_path / "nested" / "out.docx"
    copy_docx(source, dest)

    assert dest.exists()
    assert dest.read_bytes() == b"hello"

