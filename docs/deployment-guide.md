# Deployment Guide (PyInstaller)

This app is a PySide6 GUI. LibreOffice is required at runtime to perform `.doc → .docx` conversions.

## Prereqs

- Python 3.10+
- LibreOffice installed
- Install deps:

```bash
python3 -m pip install -e .
python3 -m pip install pyinstaller
```

## Build (Windows)

```bash
pyinstaller --noconfirm --clean --windowed --name batch-doc-to-docx-gui src/app.py
```

Output: `dist/batch-doc-to-docx-gui/`

LibreOffice note:
- Common `soffice` path: `C:\\Program Files\\LibreOffice\\program\\soffice.exe`
- Users can also browse to `soffice.exe` in the GUI.

## Build (macOS)

```bash
pyinstaller --noconfirm --clean --windowed --name batch-doc-to-docx-gui src/app.py
```

Output: `dist/batch-doc-to-docx-gui.app`

LibreOffice note:
- Common `soffice` path: `/Applications/LibreOffice.app/Contents/MacOS/soffice`

## Known Issues / Tips

- LibreOffice can “succeed” but not produce output; the app verifies the expected `.docx` exists.
- If conversion fails for a file, processing continues and the error is logged.
- Cancel is cooperative: it stops before starting the next file (not mid-conversion).

