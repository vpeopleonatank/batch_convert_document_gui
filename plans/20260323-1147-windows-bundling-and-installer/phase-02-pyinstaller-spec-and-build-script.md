# Phase 02 — PyInstaller spec + build script

## Context Links

- Existing docs baseline: `docs/deployment-guide.md`
- Entry point: `src/app.py`
- Dependencies: `pyproject.toml` (PySide6)

## Overview

Priority: High  
Status: COMPLETE  
Goal: make Windows builds reproducible via a checked-in PyInstaller spec + a simple build script.

## Key Insights

- A `.spec` file prevents “works on my machine” drift (hiddenimports, collected Qt plugins).
- A PowerShell build script makes it easy to build on a clean Windows box and in CI.

## Requirements

Functional:
- Provide `pyinstaller` config that:
  - builds windowed GUI (no console)
  - emits predictable output name
  - optionally includes icon + version info
- Provide a single build command/script for Windows that:
  - creates/uses a venv
  - installs deps
  - runs PyInstaller
  - zips output for distribution
  - (optional) bundles LibreOffice into the dist folder (from a `.msi`)

Non-functional:
- Keep config small + readable (YAGNI)
- Keep any new scripts under ~200 LOC

## Architecture

Packaging artifacts:
- `packaging/pyinstaller/batch-doc-to-docx-gui.spec` (implemented)
- `scripts/build-windows.ps1` (implemented)

Spec responsibilities:
- Set `name`, `windowed`, collect PySide6 resources/plugins if required
- Optionally configure `icon` and Windows version resource

## Related Code Files

Modify:
- `docs/deployment-guide.md`

Created:
- `packaging/pyinstaller/batch-doc-to-docx-gui.spec`
- `scripts/build-windows.ps1`
- (optional) `packaging/windows/version-info.txt` (or `.py` version resource)
- (optional) `assets/app-icon.ico`

Delete:
- none

## Implementation Steps

1. Add `packaging/pyinstaller/*.spec` with:
   - `Analysis([ "src/app.py" ], pathex=[...])`
   - `console=False`
   - `hiddenimports` only if build proves it’s needed (start minimal)
2. Add `scripts/build-windows.ps1`:
   - `py -3.12 -m venv .venv` (or configurable)
   - `python -m pip install --upgrade pip`
   - `python -m pip install . pyinstaller`
   - `pyinstaller packaging/pyinstaller/<name>.spec`
   - zip `dist/<name>/` to `dist/<name>-windows-x64.zip`
   - optional: `-LibreOfficeMsiPath`/`-LibreOfficeMsiUrl` bundles `LibreOffice/` into `dist/<name>/`
3. Update `docs/deployment-guide.md` to point to the script/spec instead of a raw command.
4. Smoke test on Windows:
   - launches
   - file dialogs work
   - browsing to `soffice.exe` works

## Todo List

- [x] Output naming: `batch-doc-to-docx-gui` + `-windows-x64.zip`
- [x] Version stamping: skipped (no Windows version resource yet; YAGNI)
- [x] Baseline packaging: folder build + portable zip (no `--onefile`)
- [x] Icon: default (no custom `.ico`)

## Success Criteria

- On a fresh Windows machine: `powershell -ExecutionPolicy Bypass -File scripts/build-windows.ps1` produces `dist/batch-doc-to-docx-gui-windows-x64.zip`.

## Risk Assessment

- PyInstaller + Qt sometimes requires extra collection flags; start minimal, add only when build proves missing DLL/plugin.

## Security Considerations

- Build scripts must not download or execute untrusted binaries.
- If zipping artifacts, avoid bundling extra files like `.env`, user config, logs.

## Next Steps

- If installer is needed, proceed to Phase 03.
- If CI is needed, proceed to Phase 04.
