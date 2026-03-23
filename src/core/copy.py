from __future__ import annotations

import shutil
from pathlib import Path


def copy_docx(source_docx: Path, dest_docx: Path) -> None:
    dest_docx.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_docx, dest_docx)

