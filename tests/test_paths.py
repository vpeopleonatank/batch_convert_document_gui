from pathlib import Path

import pytest

from src.core.paths import ensure_within_root, map_dest_path_for_source


def test_map_dest_path_preserves_relative_tree_and_changes_suffix():
    source_root = Path("C:/in")
    dest_root = Path("D:/out")
    source_file = Path("C:/in/a/b/file.doc")
    assert map_dest_path_for_source(source_root, dest_root, source_file, ".docx") == Path(
        "D:/out/a/b/file.docx"
    )


def test_ensure_within_root_rejects_escape():
    root = Path("/dest")
    with pytest.raises(ValueError):
        ensure_within_root(root, Path("/dest/../evil/out.docx"))

