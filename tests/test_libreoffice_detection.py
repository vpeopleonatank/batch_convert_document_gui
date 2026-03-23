from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

import src.core.libreoffice as libreoffice
from src.core.libreoffice import resolve_soffice_path


def test_resolve_soffice_path_returns_user_path_when_exists(tmp_path: Path):
    fake_soffice = tmp_path / ("soffice.exe" if os.name == "nt" else "soffice")
    fake_soffice.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    if os.name != "nt":
        fake_soffice.chmod(0o755)

    assert resolve_soffice_path(str(fake_soffice)) == fake_soffice


def test_resolve_soffice_path_can_use_bundled_libreoffice_when_frozen(monkeypatch, tmp_path: Path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    exe = app_dir / "batch-doc-to-docx-gui.exe"
    exe.write_text("", encoding="utf-8")

    bundled_soffice = app_dir / "LibreOffice" / "program" / "soffice.exe"
    bundled_soffice.parent.mkdir(parents=True)
    bundled_soffice.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    bundled_soffice.chmod(0o755)

    monkeypatch.setattr(libreoffice.shutil, "which", lambda _name: None)
    monkeypatch.setattr(sys, "executable", str(exe))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(platform, "system", lambda: "Windows")

    assert resolve_soffice_path(None) == bundled_soffice


def test_resolve_soffice_path_can_return_none_when_not_found():
    result = resolve_soffice_path(None)
    assert result is None or (isinstance(result, Path) and result.exists())
