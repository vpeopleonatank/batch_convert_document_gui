from __future__ import annotations

from pathlib import Path

from src.core.pipeline import build_work_items


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


def test_build_work_items_maps_convert_and_optional_copy(tmp_path: Path):
    source_root = tmp_path / "in"
    dest_root = tmp_path / "out"

    _touch(source_root / "a" / "one.doc")
    _touch(source_root / "a" / "two.docx")
    _touch(source_root / "a" / "ignore.txt")

    items_no_copy = build_work_items(source_root, dest_root, copy_existing_docx=False)
    assert [(i.kind, i.dest_file.relative_to(dest_root).as_posix()) for i in items_no_copy] == [
        ("convert", "a/one.docx")
    ]

    items_copy = build_work_items(source_root, dest_root, copy_existing_docx=True)
    assert [(i.kind, i.dest_file.relative_to(dest_root).as_posix()) for i in items_copy] == [
        ("convert", "a/one.docx"),
        ("copy", "a/two.docx"),
    ]

