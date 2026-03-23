# Phase 01 — Project scaffolding

## Overview

Priority: High
Status: COMPLETE
Goal: create minimal repo structure for a small PySide6 app with a clean `core/` vs `ui/` split.

## Requirements

- Keep modules small (<200 LOC).
- KISS: no plugin architecture.

## Related Code Files

Create:
- `src/app.py`
- `src/core/scan.py`
- `src/core/libreoffice.py`
- `src/core/convert.py`
- `src/core/copy.py`
- `src/ui/main_window.py`
- `src/ui/worker.py`
- `pyproject.toml` (or `requirements.txt`)

## Implementation Steps

1. Add `src/` package structure and minimal entrypoint.
2. Add config constants (supported extensions, overwrite mode).
3. Add logging helper to unify UI log append behavior.

## Todo List

- [ ] Define folder layout + imports
- [ ] Decide packaging tool (PyInstaller baseline)

## Success Criteria

- App launches to an empty shell window (no conversion yet).

## Risk Assessment

- None.

## Security Considerations

- Ensure paths are treated as data (no shell=True).

## Next Steps

- Start Phase 02.
