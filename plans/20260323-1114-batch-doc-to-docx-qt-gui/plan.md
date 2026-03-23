# Plan — Batch DOC → DOCX Qt GUI

Date: 2026-03-23
Design: `docs/plans/2026-03-23-batch-doc-to-docx-qt-gui-design.md`

## Phases

- Phase 01 — Project scaffolding (COMPLETE) → `phase-01-project-scaffolding.md`
- Phase 02 — Core conversion pipeline (COMPLETE) → `phase-02-core-conversion-pipeline.md`
- Phase 03 — Qt GUI + worker thread (COMPLETE) → `phase-03-qt-gui-and-worker-thread.md`
- Phase 04 — Packaging + docs (COMPLETE) → `phase-04-packaging-and-docs.md`

## Dependencies

- Python 3.10+ (target)
- Qt for Python: PySide6
- LibreOffice installed (or bundled/located) and `soffice` accessible

## Validation

- Unit tests for path mapping + scanning
- Manual smoke test on Windows and macOS with sample folders
