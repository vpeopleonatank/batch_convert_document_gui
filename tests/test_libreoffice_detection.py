from __future__ import annotations

import os
from pathlib import Path

from src.core.libreoffice import resolve_soffice_path


def test_resolve_soffice_path_returns_user_path_when_exists(tmp_path: Path):
    fake_soffice = tmp_path / ("soffice.exe" if os.name == "nt" else "soffice")
    fake_soffice.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    if os.name != "nt":
        fake_soffice.chmod(0o755)

    assert resolve_soffice_path(str(fake_soffice)) == fake_soffice


def test_resolve_soffice_path_can_return_none_when_not_found():
    result = resolve_soffice_path(None)
    assert result is None or (isinstance(result, Path) and result.exists())
