# File Index: Batch Convert Document GUI

Quick reference for all relevant files organized by function.

## Core Logic (`src/core/`) — No Qt Dependencies

| File | Lines | Responsibility |
|------|-------|-----------------|
| `/mnt/Data/Code/Python/batch_convert_document_gui/src/core/pipeline.py` | 155 | Main orchestration: scan → build work items → convert/copy files |
| `/mnt/Data/Code/Python/batch_convert_document_gui/src/core/convert.py` | 34 | LibreOffice subprocess wrapper (soffice --convert-to docx) |
| `/mnt/Data/Code/Python/batch_convert_document_gui/src/core/scan.py` | 16 | Recursive file discovery (.doc, .docx) with sorting |
| `/mnt/Data/Code/Python/batch_convert_document_gui/src/core/paths.py` | 22 | Path mapping & safety (prevent traversal) |
| `/mnt/Data/Code/Python/batch_convert_document_gui/src/core/libreoffice.py` | 54 | Cross-platform soffice detection |
| `/mnt/Data/Code/Python/batch_convert_document_gui/src/core/copy.py` | 10 | File copy with parent directory creation |
| `/mnt/Data/Code/Python/batch_convert_document_gui/src/core/work_items.py` | 15 | WorkItem dataclass (convert/copy enum) |

## UI Components (`src/ui/`) — PySide6/Qt

| File | Lines | Responsibility |
|------|-------|-----------------|
| `/mnt/Data/Code/Python/batch_convert_document_gui/src/ui/main_window.py` | 199 | Main window: form, inputs, progress, logs, threading |
| `/mnt/Data/Code/Python/batch_convert_document_gui/src/ui/worker.py` | 53 | QThread worker: runs pipeline, emits signals |
| `/mnt/Data/Code/Python/batch_convert_document_gui/src/ui/widgets.py` | 33 | LogTextEdit, make_browse_row helper |
| `/mnt/Data/Code/Python/batch_convert_document_gui/src/app.py` | 24 | QApplication entry point |

## Tests

| File | Purpose |
|------|---------|
| `/mnt/Data/Code/Python/batch_convert_document_gui/tests/test_sanity_imports.py` | Basic imports work |
| `/mnt/Data/Code/Python/batch_convert_document_gui/tests/test_scan.py` | File discovery logic |
| `/mnt/Data/Code/Python/batch_convert_document_gui/tests/test_paths.py` | Path mapping & safety |
| `/mnt/Data/Code/Python/batch_convert_document_gui/tests/test_libreoffice_detection.py` | soffice discovery |
| `/mnt/Data/Code/Python/batch_convert_document_gui/tests/test_convert_smoke.py` | Subprocess integration |
| `/mnt/Data/Code/Python/batch_convert_document_gui/tests/test_copy.py` | File copy |
| `/mnt/Data/Code/Python/batch_convert_document_gui/tests/test_pipeline_mapping.py` | Work item building |
| `/mnt/Data/Code/Python/batch_convert_document_gui/tests/conftest.py` | pytest config |

## Configuration & Docs

| File | Purpose |
|------|---------|
| `/mnt/Data/Code/Python/batch_convert_document_gui/pyproject.toml` | Build, dependencies, pytest config |
| `/mnt/Data/Code/Python/batch_convert_document_gui/README.md` | Quick start & usage |
| `/mnt/Data/Code/Python/batch_convert_document_gui/docs/deployment-guide.md` | Installation & setup |

## Planning Documents

| File | Purpose |
|------|---------|
| `/mnt/Data/Code/Python/batch_convert_document_gui/plans/20260323-1114-batch-doc-to-docx-qt-gui/plan.md` | Overview of 4 phases |
| `/mnt/Data/Code/Python/batch_convert_document_gui/plans/20260323-1114-batch-doc-to-docx-qt-gui/phase-01-project-scaffolding.md` | Project structure setup |
| `/mnt/Data/Code/Python/batch_convert_document_gui/plans/20260323-1114-batch-doc-to-docx-qt-gui/phase-02-core-conversion-pipeline.md` | Core logic implementation |
| `/mnt/Data/Code/Python/batch_convert_document_gui/plans/20260323-1114-batch-doc-to-docx-qt-gui/phase-03-qt-gui-and-worker-thread.md` | UI & threading |
| `/mnt/Data/Code/Python/batch_convert_document_gui/plans/20260323-1114-batch-doc-to-docx-qt-gui/phase-04-packaging-and-docs.md` | Packaging & documentation |

---

## Quick Command Reference

```bash
# Run the app
python3 -m src.app

# Run all tests
pytest -q

# Check syntax
python3 -m compileall -q src

# Install (dev)
python3 -m pip install -e '.[dev]'
```

---

## File Groups by Feature

### Conversion Pipeline
- `src/core/pipeline.py` — Orchestration
- `src/core/convert.py` — soffice integration
- `src/core/scan.py` — File discovery

### Path Handling
- `src/core/paths.py` — Mapping & safety
- `src/core/copy.py` — File operations

### LibreOffice Detection
- `src/core/libreoffice.py` — Cross-platform soffice resolver

### Threading & UI
- `src/ui/worker.py` — Worker thread
- `src/ui/main_window.py` — Main window & form
- `src/ui/widgets.py` — Reusable widgets

### Testing
- All `tests/test_*.py` files
- `tests/conftest.py` — Configuration

