from __future__ import annotations

from pathlib import Path


def map_dest_path_for_source(
    source_root: Path,
    dest_root: Path,
    source_file: Path,
    dest_suffix: str,
) -> Path:
    relative = source_file.relative_to(source_root)
    return (dest_root / relative).with_suffix(dest_suffix)


def ensure_within_root(root: Path, path: Path) -> Path:
    root_resolved = root.resolve(strict=False)
    path_resolved = path.resolve(strict=False)
    if root_resolved not in [path_resolved, *path_resolved.parents]:
        raise ValueError("Destination path escapes destination root")
    return path_resolved

