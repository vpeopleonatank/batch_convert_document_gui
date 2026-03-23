# Architecture Summary: Batch Convert Document GUI

**Quick visual reference for system design.**

---

## System Layers

```
┌─────────────────────────────────────────┐
│         Qt GUI Layer (src/ui/)          │
├─────────────────────────────────────────┤
│ MainWindow (QMainWindow)                │
│  ├─ Form: source, dest, soffice, etc.  │
│  ├─ Buttons: Start, Cancel             │
│  ├─ Progress bar, current file, logs   │
│  └─ Manages Worker thread              │
├─────────────────────────────────────────┤
│ Worker (QObject on QThread)             │
│  └─ Calls run_pipeline() off main thread│
├─────────────────────────────────────────┤
│ Widgets & Helpers                       │
│  ├─ LogTextEdit (read-only text edit)  │
│  └─ make_browse_row() (layout helper)  │
└─────────────────────────────────────────┘
           (Qt dependencies)
                   │
                   │ calls
                   ↓
┌─────────────────────────────────────────┐
│    Core Pipeline Layer (src/core/)      │
├─────────────────────────────────────────┤
│ pipeline.py                             │
│  ├─ run_pipeline() ← main entry         │
│  └─ build_work_items()                 │
├─────────────────────────────────────────┤
│ Data Models                             │
│  └─ WorkItem (frozen dataclass)        │
│  └─ PipelineSummary (frozen dataclass) │
├─────────────────────────────────────────┤
│ Workers                                 │
│  ├─ convert_doc_to_docx() → soffice    │
│  └─ copy_docx() → shutil.copy2         │
├─────────────────────────────────────────┤
│ Utilities                               │
│  ├─ scan_files() → recursion           │
│  ├─ map_dest_path_for_source() → str  │
│  ├─ ensure_within_root() → validation  │
│  └─ resolve_soffice_path() → detection │
└─────────────────────────────────────────┘
    (NO Qt dependencies - reusable)
                   │
                   │ spawns
                   ↓
┌─────────────────────────────────────────┐
│        External Processes               │
├─────────────────────────────────────────┤
│ soffice (LibreOffice headless)          │
│  └─ Converts .doc to .docx             │
└─────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
User Input (QLineEdit)
├─ source_dir: Path
├─ dest_dir: Path
├─ soffice_path: Path
└─ copy_existing_docx: bool
        ↓
    MainWindow
        ↓
    Worker.run()
        ↓
    run_pipeline(source_dir, dest_dir, ...)
        ├─ scan_files(source_dir)
        │  └─ [Path, Path, ...]
        ├─ build_work_items()
        │  └─ [WorkItem(kind="convert"|"copy", source, dest), ...]
        └─ for item in work_items:
           ├─ is_cancelled() → break if true
           ├─ emit on_current_file(str)
           ├─ if item.kind == "convert":
           │  └─ convert_doc_to_docx(soffice_path, source, dest_dir)
           │     └─ subprocess.run(["soffice", "--headless", ...])
           │        └─ emit on_log(result)
           ├─ else (copy):
           │  └─ copy_docx(source, dest)
           │     └─ shutil.copy2(source, dest)
           │        └─ emit on_log(result)
           └─ emit on_progress(total, done)
        ↓
    return PipelineSummary
        ↓
    Worker.finished.emit(summary)
        ↓
    MainWindow._on_finished(summary)
        └─ Show dialog + update UI
```

---

## Module Dependency Graph

```
src/ui/main_window.py
├─ imports: ui/worker.py
├─ imports: ui/widgets.py
├─ imports: core/libreoffice.py (detect soffice)
└─ calls: Worker.run() via QThread

src/ui/worker.py
├─ imports: core/pipeline.py
└─ emits Qt signals

src/ui/widgets.py
└─ pure Qt widgets (no core imports)

src/app.py
└─ imports: ui/main_window.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

src/core/pipeline.py
├─ imports: convert.py
├─ imports: copy.py
├─ imports: paths.py
├─ imports: scan.py
└─ imports: work_items.py

src/core/convert.py
└─ subprocess.run(soffice)

src/core/copy.py
└─ shutil.copy2()

src/core/scan.py
└─ Path.rglob()

src/core/paths.py
└─ Path operations

src/core/libreoffice.py
└─ detect soffice (Path, platform checks)

src/core/work_items.py
└─ dataclass definitions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No circular dependencies detected.
```

---

## Threading Model

```
Qt Main Thread
│
├─ QApplication.exec() [blocked, waiting for events]
│
├─ User clicks "Start"
│  └─ _on_start_clicked()
│     ├─ Create QThread
│     ├─ Create Worker (QObject)
│     ├─ worker.moveToThread(thread)
│     ├─ Connect signals: thread.started → worker.run()
│     ├─ Connect signals: worker.progress → _on_progress()
│     ├─ Connect signals: worker.finished → _on_finished()
│     └─ thread.start()
│
└─ Wait for signals from Worker
   │
   ├─ [Worker Thread running in parallel]
   │  │
   │  └─ worker.run()
   │     └─ run_pipeline() [blocking]
   │        └─ For each file:
   │           └─ Emit signals back to MainWindow
   │
   └─ Receive signals (thread-safe via Qt event loop)
      ├─ worker.progress → update progress bar
      ├─ worker.log → append to log
      ├─ worker.current_file → update label
      ├─ worker.finished → show dialog
      └─ thread.quit() → cleanup
```

**Key insight:** Signals automatically marshal data from worker thread back to main thread. No explicit locking needed.

---

## Error Handling Strategy

```
run_pipeline()
│
└─ for item in work_items:
   │
   ├─ try:
   │  └─ if item.kind == "convert":
   │     ├─ convert_doc_to_docx()
   │     └─ if success: increment converted
   │     └─ else: increment failed (continue)
   │  else:
   │     ├─ copy_docx()
   │     └─ increment copied (or failed on exception)
   │
   └─ except Exception as exc:
      └─ log(error)
         └─ increment failed
            └─ continue (don't stop processing)
```

**Principle:** Maximize completion. If one file fails, process remaining files.

---

## State Transitions (MainWindow)

```
Startup
  ├─ detect soffice (auto)
  └─ _refresh_start_enabled()

Idle State (Start enabled)
  ├─ User fills in source & dest
  ├─ Start button becomes enabled
  └─ User clicks Start

Running State (Cancel enabled)
  ├─ Worker thread processes files
  ├─ Signals update UI (progress, logs)
  ├─ User can click Cancel anytime
  │  └─ Sets Worker._cancel_requested = True
  │     └─ Pipeline checks before next file
  └─ Worker finishes (or cancelled)

Finished State (cleanup)
  ├─ Cleanup worker & thread
  ├─ _refresh_start_enabled()
  ├─ Show summary dialog
  └─ Back to Idle State
```

---

## Cross-Platform Considerations

### LibreOffice Detection (`libreoffice.py`)

1. Check user-provided path
2. Check `shutil.which("soffice")`
3. Platform-specific hardcoded paths:
   - **macOS:** `/Applications/LibreOffice.app/Contents/MacOS/soffice`
   - **Windows:** `C:\Program Files\LibreOffice\program\soffice.exe` (or 32-bit variant)
   - **Linux:** `/usr/bin/soffice`, `/usr/local/bin/soffice`, `/snap/bin/libreoffice`

### Path Handling (`paths.py`)

- **Map destination:** Preserves folder structure via `relative_to()` + `with_suffix()`
- **Prevent traversal:** `ensure_within_root()` validates path is within destination

### File Operations

- **Scan:** `Path.rglob()` (cross-platform recursion)
- **Copy:** `shutil.copy2()` (preserves metadata)
- **Convert:** `subprocess.run()` with platform-agnostic list syntax

---

## Testability

### Testable Layers

| Layer | Testability | Notes |
|-------|-----------|-------|
| Core pipeline | ✓ Excellent | No external deps (except soffice) |
| Path mapping | ✓ Excellent | Pure functions |
| File scanning | ✓ Excellent | File system only |
| soffice detection | ✓ Excellent | Platform checks & mocking |
| UI components | ◐ Moderate | Requires Qt; signals hard to test |
| Threading | ◐ Moderate | Requires Qt event loop simulation |

### Test Strategy

- **Unit tests** for core logic (scan, paths, convert, copy)
- **Smoke tests** for integration (requires actual soffice)
- **Manual tests** for UI (threading, signals, user interactions)

---

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Scanning | O(n) | One pass through file tree |
| Building work items | O(n) | Linear iteration |
| Conversion | O(n×m) | n files, m seconds per conversion |
| Copying | O(n×s) | n files, s bytes per file |

**Bottleneck:** soffice subprocess (time per file conversion).

**Improvement opportunity:** Parallel processing (multiple soffice instances).

---

## Summary

✓ **Clean separation:** Core logic (testable, reusable) + UI (responsive, user-friendly)
✓ **Threading:** Qt signals eliminate manual locking
✓ **Error handling:** Per-file, continue processing
✓ **Cross-platform:** Tested paths for Windows, macOS, Linux
✓ **Extensible:** Easy to add new formats or UI options

