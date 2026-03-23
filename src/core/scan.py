from __future__ import annotations

from pathlib import Path

SUPPORTED_SUFFIXES = {".doc", ".docx"}


def scan_files(source_dir: Path) -> list[Path]:
    files: list[Path] = []
    for candidate in source_dir.rglob("*"):
        if not candidate.is_file():
            continue
        if candidate.suffix.lower() in SUPPORTED_SUFFIXES:
            files.append(candidate)
    return sorted(files, key=lambda p: str(p).lower())

