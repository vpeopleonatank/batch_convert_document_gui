# Batch DOC → DOCX Converter (Qt GUI)

Cross-platform (Windows/macOS) desktop GUI to recursively convert `.doc` → `.docx` using LibreOffice headless, and optionally copy existing `.docx` files to a destination folder while preserving folder structure.

## Requirements

- Python 3.10+
- LibreOffice installed (`soffice` available or browsable in the app)

## Install (dev)

```bash
python3 -m pip install -e '.[dev]'
```

## Run

```bash
python3 -m src.app
```

## Test

```bash
pytest -q
python3 -m compileall -q src
```

## Packaging / Deployment

See `docs/deployment-guide.md` (PyInstaller + Windows GitHub Actions workflow).

## Usage

1. Pick a source folder and destination folder.
2. (Optional) enable “Copy existing .docx”.
3. Ensure LibreOffice `soffice` is detected (or browse to it).
4. Start. Use Cancel to stop between files (best-effort).
