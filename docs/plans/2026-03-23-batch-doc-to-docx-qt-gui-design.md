# Batch DOC → DOCX Converter (Qt GUI) — Design

Date: 2026-03-23
Project: `batch_convert_document_gui`

## Context

Repo was empty at design time (no `README.md`, `CLAUDE.md`, `docs/` initially).

Goal: a cross-platform desktop GUI (Windows first, also macOS) to batch convert `.doc` to `.docx` in a folder tree and optionally copy existing `.docx` files to a destination folder.

## Decisions (Approved)

- Conversion backend: **LibreOffice headless** (`soffice --headless`).
- Folder traversal: **recursive**.
- Destination conflict policy: **overwrite**.
- File types:
  - Convert: `.doc` → `.docx`
  - Copy (optional via checkbox): `.docx` → `.docx`

## Non-goals (YAGNI)

- No `.pdf`, `.rtf`, `.odt` support in v1.
- No live preview.
- No OCR.
- No Word COM automation fallback.

## UX / Screens

Main window:
- Source folder picker
- Destination folder picker
- Checkbox: “Copy existing .docx”
- LibreOffice executable:
  - auto-detect + “Browse…” override
- Start + Cancel
- Progress bar + current file label
- Log panel (append-only text)
- Summary at end: scanned/converted/copied/failed/skipped + duration

## Core Behavior

1. Scan source folder recursively for `.doc` and `.docx` (case-insensitive).
2. For each `.doc`:
   - Convert via LibreOffice headless into destination folder, preserving relative path.
   - Ensure destination subfolders exist.
   - Overwrite existing `.docx` in destination.
3. For each `.docx`:
   - If checkbox enabled, copy to destination preserving relative path.
   - Overwrite existing destination file.
4. If Cancel pressed:
   - Stop after current file finishes (best-effort cooperative cancel).
5. Errors:
   - Continue processing remaining files.
   - Record per-file failures in log + summary counts.

## Architecture (Modules)

- `core/scan.py`: walk tree, filter extensions, compute relative output paths
- `core/convert.py`: `subprocess` wrapper for LibreOffice conversion
- `core/copy.py`: `.docx` copy helper (`shutil.copy2`)
- `core/libreoffice.py`: detect `soffice` path across platforms (Windows/macOS/Linux)
- `ui/main_window.py`: Qt widgets
- `ui/worker.py`: `QThread` worker emitting progress + log signals

Guideline: keep each file <200 LOC; split early.

## LibreOffice Integration Notes

Command shape (conceptual):
- `soffice --headless --nologo --nodefault --nolockcheck --norestore --convert-to docx --outdir <dest_dir> <source_doc>`

Notes:
- Use per-file output directory corresponding to the destination file’s folder to preserve structure.
- Validate `soffice` exists and is executable before starting.
- Capture stdout/stderr for logging and diagnosing failures.

## Platform Notes

- Windows: prefer `soffice.exe` discovery + user browse.
- macOS: allow `.../LibreOffice.app/Contents/MacOS/soffice`.

## Success Criteria

- Converts `.doc` recursively into destination, preserving tree structure.
- Optional `.docx` copy works.
- Overwrite behavior matches expectation.
- Cancel works without crashing UI.
- Packagable for Windows and macOS (at least documented).

## Open Questions

- None (design approved as-is).

