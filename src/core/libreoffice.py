from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path


def _is_executable_file(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False

    if os.name == "nt":
        return path.suffix.lower() in {".exe", ".com", ".bat", ".cmd"} or path.suffix == ""

    return os.access(path, os.X_OK)


def resolve_soffice_path(user_path: str | None) -> Path | None:
    if user_path:
        candidate = Path(user_path).expanduser()
        return candidate if _is_executable_file(candidate) else None

    from_path = shutil.which("soffice")
    if from_path:
        candidate = Path(from_path)
        if _is_executable_file(candidate):
            return candidate

    system = platform.system().lower()
    candidates: list[Path] = []
    if system == "darwin":
        candidates.append(Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"))
    elif system == "windows":
        candidates.extend(
            [
                Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
                Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
            ]
        )
    else:
        candidates.extend(
            [
                Path("/usr/bin/soffice"),
                Path("/usr/local/bin/soffice"),
                Path("/snap/bin/libreoffice"),
            ]
        )

    for candidate in candidates:
        if _is_executable_file(candidate):
            return candidate
    return None

