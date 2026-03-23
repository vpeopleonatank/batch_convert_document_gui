# Deployment Guide (PyInstaller)

This app is a PySide6 GUI. LibreOffice is required at runtime to perform `.doc → .docx` conversions.

## Prereqs

- Python 3.10+
- Build on the target OS (no cross-compile)
- LibreOffice installed

## Build (Windows)

Build script: `scripts/build-windows.ps1` (creates `.venv/`, installs deps, runs `packaging/pyinstaller/batch-doc-to-docx-gui.spec`, zips `dist/*.zip`).

```pwsh
powershell -ExecutionPolicy Bypass -File scripts/build-windows.ps1 -PythonExe "python" -Arch "x64"
# If you want to use the Python Launcher:
# powershell -ExecutionPolicy Bypass -File scripts/build-windows.ps1 -PythonExe "py" -PythonArgs @("-3.12") -Arch "x64"
```

Output:
- Folder: `dist/batch-doc-to-docx-gui/`
- Portable zip: `dist/batch-doc-to-docx-gui-windows-x64.zip`

### Bundle LibreOffice into the zip (optional)

If you want a self-contained zip (no LibreOffice install required), pass a LibreOffice `.msi`:

```pwsh
powershell -ExecutionPolicy Bypass -File scripts/build-windows.ps1 -PythonExe "python" -Arch "x64" -LibreOfficeMsiPath "C:\\path\\to\\LibreOffice_x.y.z_Win_x86-64.msi"
```

Or provide a direct `.msi` URL:

```pwsh
powershell -ExecutionPolicy Bypass -File scripts/build-windows.ps1 -PythonExe "python" -Arch "x64" -LibreOfficeMsiUrl "https://example.com/LibreOffice.msi"
```

Note: this makes the zip very large; ensure your redistribution complies with LibreOffice licensing.

LibreOffice note:
- Common `soffice` path: `C:\\Program Files\\LibreOffice\\program\\soffice.exe`
- Users can also browse to `soffice.exe` in the GUI.

## Build (GitHub Actions)

Workflow: `.github/workflows/build-windows.yml`

      - Manual run: Actions → `build-windows` → Run workflow → download artifact
      - Tag build: push a tag like `v0.1.0` (`v*`) and the workflow uploads the portable zip artifact

To bundle LibreOffice in CI, set repo variable `LIBREOFFICE_MSI_URL` to a direct `.msi` URL.

## Build (macOS)

```bash
python3 -m pip install . pyinstaller
python3 -m PyInstaller --noconfirm --clean packaging/pyinstaller/batch-doc-to-docx-gui.spec
```

Output: `dist/batch-doc-to-docx-gui/`

LibreOffice note:
- Common `soffice` path: `/Applications/LibreOffice.app/Contents/MacOS/soffice`

## Known Issues / Tips

- LibreOffice can “succeed” but not produce output; the app verifies the expected `.docx` exists.
- If conversion fails for a file, processing continues and the error is logged.
- Cancel is cooperative: it stops before starting the next file (not mid-conversion).
