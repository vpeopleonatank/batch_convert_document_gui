from __future__ import annotations

from pathlib import Path

from src.core.scan import scan_files


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


def test_scan_files_finds_doc_and_docx_sorted(tmp_path: Path):
    source_root = tmp_path / "in"
    _touch(source_root / "a" / "file1.doc")
    _touch(source_root / "a" / "file2.docx")
    _touch(source_root / "a" / "ignore.txt")
    _touch(source_root / "b" / "Z.DOC")

    scanned = scan_files(source_root)
    assert [p.name for p in scanned] == ["file1.doc", "file2.docx", "Z.DOC"]

