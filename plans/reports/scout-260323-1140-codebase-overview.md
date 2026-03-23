# Scout Report: Batch Convert Document GUI - Codebase Overview

**Date:** 2026-03-23 | **Project:** batch_convert_document_gui

## Executive Summary

This is a complete, functional cross-platform (Windows/macOS) desktop GUI application built with PySide6 (Qt) that recursively converts `.doc` → `.docx` files using LibreOffice headless, with optional `.docx` copying. All phases (scaffolding, core pipeline, UI, and packaging) are complete and tested.

---

## 1. Project Structure & Dependencies

### File Organization
```
batch_convert_document_gui/
├── src/
│   ├── __init__.py
│   ├── app.py                    # Qt application entry point
│   ├── core/                     # Core business logic (no Qt dependencies)
│   │   ├── __init__.py
│   │   ├── convert.py            # LibreOffice subprocess wrapper
│   │   ├── copy.py               # File copying utility
│   │   ├── libreoffice.py        # soffice executable detection (cross-platform)
│   │   ├── paths.py              # Path mapping & destination safety checks
│   │   ├── pipeline.py           # Main orchestration (async callbacks)
│   │   ├── scan.py               # Recursive file scanner (.doc & .docx)
│   │   └── work_items.py         # WorkItem dataclass (convert/copy work)
│   └── ui/                       # PySide6 UI components
│       ├── __init__.py
│       ├── main_window.py        # QMainWindow with form layout & threading
│       ├── worker.py             # QThread worker (runs pipeline off main thread)
│       └── widgets.py            # LogTextEdit & browse_row helper
├── tests/                        # pytest-based test suite
│   ├── conftest.py              # pytest config
│   ├── test_sanity_imports.py   # Basic import smoke tests
│   ├── test_paths.py            # Path mapping validation
│   ├── test_scan.py             # File scanning tests
│   ├── test_libreoffice_detection.py  # soffice detection tests
│   ├── test_convert_smoke.py    # LibreOffice conversion smoke test
│   ├── test_copy.py             # File copy tests
│   └── test_pipeline_mapping.py # Pipeline work item building tests
├── pyproject.toml               # Build metadata, pytest config, deps
├── README.md                    # Quick start guide
├── docs/
│   ├── deployment-guide.md      # Installation & deployment
│   └── plans/                   # Design & implementation documentation
└── plans/
    └── 20260323-1114-batch-doc-to-docx-qt-gui/
        ├── plan.md              # Overview of all phases
        └── phase-0X-*.md        # 4 detailed phase documents
```

### Dependencies
- **PySide6 >=6.6** — Qt framework for cross-platform GUI
- **pytest >=7.0** — Test framework (dev only)
- **Python 3.10+** — Minimum required version

---

## 2. Core Conversion Pipeline (`src/core/`)

### 2.1 High-Level Flow

```
User provides: source_dir, dest_dir, soffice_path, copy_existing_docx flag
                ↓
scan_files(source_dir)
  → Returns sorted list of .doc & .docx files recursively
                ↓
build_work_items()
  → For each .doc: create "convert" WorkItem with mapped destination
  → For each .docx (if flag set): create "copy" WorkItem
                ↓
run_pipeline()
  → For each work item:
    ├─ convert: subprocess soffice --convert-to docx
    └─ copy: shutil.copy2() with parent creation
  → Emit progress, current file, logs during execution
  → Support cancellation via is_cancelled() callback
                ↓
Return PipelineSummary with counts (converted, copied, failed, duration)
```

### 2.2 Key Modules

**`scan.py`** — File discovery
- `scan_files(source_dir: Path) → list[Path]`
- Recursively finds `.doc` and `.docx` files
- Returns sorted list for deterministic ordering

**`paths.py`** — Destination path handling
- `map_dest_path_for_source()` — Preserves folder structure by mapping relative paths
- `ensure_within_root()` — Security check: prevents path traversal attacks

**`convert.py`** — LibreOffice integration
- `convert_doc_to_docx(soffice_path, source_doc, dest_dir) → (bool, str)`
- Spawns `soffice --headless --convert-to docx --outdir ...`
- Returns success flag and detailed subprocess log (for debugging)

**`copy.py`** — File copying
- `copy_docx(source_docx, dest_docx) → None`
- Simple wrapper: `shutil.copy2()` with parent directory creation

**`work_items.py`** — Data model
- `WorkItem` frozen dataclass with `kind: Literal["convert", "copy"]`

**`pipeline.py`** — Orchestration (core logic)
- `build_work_items()` — Creates list of WorkItem objects
- `run_pipeline()` — Main function that:
  - Accepts callbacks: `on_log`, `on_progress`, `on_current_file`, `is_cancelled`
  - Iterates through work items with cancellation support
  - Returns `PipelineSummary` (scanned, work items, converted, copied, failed, cancelled, duration)

### 2.3 Pipeline Features

✓ Folder structure preservation (relative paths mapped to dest)
✓ Destination path safety (path traversal prevention)
✓ Cross-platform soffice detection (Windows, macOS, Linux)
✓ Graceful cancellation (checked before each file)
✓ Error handling (catches exceptions per-file, continues processing)
✓ Detailed logging (subprocess output captured and reported)

---

## 3. UI Implementation (`src/ui/`)

### 3.1 Architecture: Main Thread + Worker Thread

```
Qt Main Thread
  │
  └─ MainWindow (QMainWindow)
      ├─ Form inputs: source, dest, soffice, copy_docx checkbox
      ├─ Buttons: Start, Cancel
      ├─ Progress bar (0–100%)
      ├─ Current file label
      ├─ Log text edit (read-only)
      │
      └─ Spawns QThread (when Start clicked)
          │
          └─ Worker (runs on dedicated thread)
              ├─ run_pipeline() (blocking)
              ├─ Emits signals: progress, current_file, log, finished, failed
              │
              └─ MainWindow connects to signals
                 (Qt automatically marshals back to main thread)
```

### 3.2 Components

**`main_window.py`** — Central UI window
- Form layout with: source folder, dest folder, copy checkbox, soffice path
- Browse buttons for file/folder selection
- Start/Cancel buttons with state management
- Progress bar (0–N items)
- Current file label (updates during conversion)
- Log text edit (accumulates all logs)
- Auto-detects soffice on startup
- Validates all inputs before enabling Start button
- Cleanup after worker finishes (kills thread, re-enables Start)

**`worker.py`** — Threaded pipeline executor
- `Worker(QObject)` with Qt signals for: progress, current_file, log, finished, failed
- `run()` — Called on worker thread, calls `run_pipeline()` with signal emission callbacks
- `request_cancel()` — Thread-safe flag to signal cancellation

**`widgets.py`** — Reusable UI components
- `LogTextEdit(QTextEdit)` — Read-only text edit with `append_line()` method
- `make_browse_row()` — Helper to create QHBoxLayout with QLineEdit + Browse button

**`app.py`** — Entry point
- Initializes PySide6 QApplication
- Creates and shows MainWindow
- Catches PySide6 import errors with helpful message

### 3.3 UI Features

✓ Async processing (worker thread prevents UI freezing)
✓ Real-time progress display (item N of M)
✓ Live log streaming (one line per file processed)
✓ Current file tracking (shows which file is being processed)
✓ Cancellation support (user can stop between files)
✓ Input validation (Start button only enabled when ready)
✓ Cross-platform soffice browsing (file dialog)
✓ Status feedback (LibreOffice detected or missing)

---

## 4. End-to-End Pipeline Flow

### 4.1 User Interaction

1. User launches app: `python3 -m src.app`
2. MainWindow opens, auto-detects soffice
3. User selects source folder (contains .doc and/or .docx)
4. User selects destination folder (may not exist)
5. (Optional) Check "Copy existing .docx"
6. (If needed) Browse to soffice manually
7. Click Start
8. Worker thread:
   - Scans source folder
   - Builds work items
   - Iterates through files
   - Emits progress & logs to main thread
9. User can click Cancel anytime
10. Finish → Summary dialog

### 4.2 Data Flow

```
QLineEdit (source) → MainWindow → Worker
                  ↓
Worker calls run_pipeline(source_dir, dest_dir, soffice_path, ...)
                  ↓
run_pipeline calls scan_files() → list[Path]
                  ↓
build_work_items() → list[WorkItem]
                  ↓
For each WorkItem:
  ├─ If kind=="convert": subprocess soffice (convert.py)
  ├─ If kind=="copy": shutil.copy2 (copy.py)
  ├─ Emit on_log() callback (MainWindow.log signal)
  ├─ Emit on_progress() callback (MainWindow.progress signal)
  ├─ Emit on_current_file() callback (MainWindow.current_file signal)
  └─ Check is_cancelled() (Worker._cancel_requested flag)
                  ↓
Return PipelineSummary (text report)
                  ↓
Worker.finished signal → MainWindow shows dialog
```

---

## 5. Test Coverage

### Test Files

| Test File | Purpose | Coverage |
|-----------|---------|----------|
| `test_sanity_imports.py` | Module imports work | Basic smoke test |
| `test_scan.py` | File scanning logic | Recursive discovery, sorting |
| `test_paths.py` | Path mapping & safety | Destination mapping, traversal prevention |
| `test_libreoffice_detection.py` | soffice discovery | Windows, macOS, Linux paths |
| `test_convert_smoke.py` | LibreOffice conversion | Subprocess integration (requires soffice) |
| `test_copy.py` | File copying | shutil integration, parent creation |
| `test_pipeline_mapping.py` | Work item building | Convert/copy work items, doc/docx splitting |

### Running Tests
```bash
pytest -q                    # Run all tests
python3 -m compileall -q src # Check syntax
```

---

## 6. Key Design Decisions

| Aspect | Design | Rationale |
|--------|--------|-----------|
| **Separation** | Core logic (no Qt) + UI (PySide6) | Testability; core can be used without GUI |
| **Threading** | QThread + Worker signals | Qt thread-safe signal-based communication |
| **Callbacks** | Pipeline accepts callbacks (not signals) | Core logic remains Qt-free |
| **Cancellation** | Check is_cancelled() before each file | Clean, best-effort stopping |
| **Path safety** | `ensure_within_root()` validation | Prevent symlink/traversal attacks |
| **Error handling** | Catch per-file, continue processing | Maximize completion even with failures |
| **Subprocess** | `soffice` headless with full args | Reliable conversion; capture output for logs |

---

## 7. Important Files at a Glance

| File | Lines | Purpose |
|------|-------|---------|
| `src/core/pipeline.py` | 155 | Main orchestration + PipelineSummary |
| `src/ui/main_window.py` | 199 | Qt MainWindow with form & thread management |
| `src/core/convert.py` | 34 | LibreOffice subprocess wrapper |
| `src/core/scan.py` | 16 | File scanner |
| `src/core/paths.py` | 22 | Path mapping & safety |
| `src/ui/worker.py` | 53 | QThread worker |
| `src/core/libreoffice.py` | 54 | Cross-platform soffice detection |
| `src/core/copy.py` | 10 | File copy wrapper |
| `src/core/work_items.py` | 15 | WorkItem dataclass |
| `src/ui/widgets.py` | 33 | LogTextEdit & browse_row |
| `pyproject.toml` | 20 | Build config, dependencies |

---

## 8. How to Extend

### Adding a New Conversion Format

1. Modify `scan.py` to include new suffix in `SUPPORTED_SUFFIXES`
2. Modify `pipeline.py` `build_work_items_from_scanned()` to handle new suffix
3. Add conversion logic in `convert.py` (or new module)
4. Update tests

### Adding a New Option to the UI

1. Add QWidget (checkbox, spinbox, etc.) to `MainWindow.__init__`
2. Pass value to Worker in `_on_start_clicked()`
3. Pass to `run_pipeline()` in `worker.py`
4. Use in pipeline logic

### Modularizing Large Files

- `main_window.py` (199 lines) is approaching 200-line threshold
  - Could split form layout into separate module
  - Could extract file browser logic into separate class
- Currently acceptable given clarity; monitor for future growth

---

## 9. Known Limitations & Notes

- **LibreOffice required** — Headless conversion requires soffice binary
- **Cancellation best-effort** — Stops before next file, not mid-conversion
- **Single-threaded pipeline** — Processes one file at a time (could be parallelized)
- **No progress estimation** — Progress bar is item-based (0–N), not time-based
- **Limited error recovery** — Conversion failures don't retry
- **Platform-specific paths** — soffice detection hardcoded for Windows/macOS/Linux

---

## 10. Unresolved Questions

None identified during scouting. Codebase is complete and functional.

---

## Summary

This is a **mature, well-structured project** with clean separation between core logic and UI:

✓ Core pipeline is Qt-independent and fully testable
✓ UI is responsive (worker thread prevents blocking)
✓ Cross-platform (Windows, macOS, Linux soffice detection)
✓ Comprehensive error handling and logging
✓ Test suite covers key functionality
✓ Clear code organization and documentation

**Ready for:** Feature enhancements, testing on multiple platforms, deployment, or use as a library.

