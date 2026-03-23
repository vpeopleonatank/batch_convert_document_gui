# Batch DOC → DOCX (Qt GUI) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a cross-platform (Windows + macOS) PySide6 desktop app that recursively converts `.doc` to `.docx` using LibreOffice headless, and optionally copies `.docx` files to a destination folder, preserving folder structure and overwriting conflicts.

**Architecture:** Keep all non-UI logic in `src/core/` (scan, mapping, LibreOffice detection, conversion, copying). UI lives in `src/ui/` and runs work in a `QThread` worker emitting progress + log signals.

**Tech Stack:** Python 3.10+, PySide6, pytest, PyInstaller, LibreOffice (`soffice --headless`).

---

## Pre-flight (do before Task 1)

- Create a dedicated git worktree/branch for implementation.
- Install LibreOffice on dev machine and confirm `soffice` runs.
- Decide dependency management:
  - Preferred: `pyproject.toml` + `pip install -e .`
  - Alternative: `requirements.txt`

---

### Task 1: Create minimal project layout

**Files:**
- Create: `src/app.py`
- Create: `src/core/__init__.py`
- Create: `src/ui/__init__.py`
- Create: `pyproject.toml`

**Step 1: Write the failing test**

Create: `tests/test_sanity_imports.py`
```python
def test_imports_work():
    import src  # noqa: F401
```

**Step 2: Run test to verify it fails**

Run: `pytest -q`
Expected: FAIL (module/package missing).

**Step 3: Write minimal implementation**

- Add `src/` package layout compatible with tests.
- Keep `src/app.py` as a placeholder entrypoint (no GUI yet).

**Step 4: Run test to verify it passes**

Run: `pytest -q`
Expected: PASS.

**Step 5: Compile check**

Run: `python -m compileall -q src`
Expected: exit 0.

---

### Task 2: Implement path mapping (pure function)

**Files:**
- Create: `src/core/paths.py`
- Test: `tests/test_paths.py`

**Step 1: Write the failing test**
```python
from pathlib import Path

from src.core.paths import map_dest_path_for_source

def test_map_dest_path_preserves_relative_tree_and_changes_suffix():
    source_root = Path("C:/in")
    dest_root = Path("D:/out")
    source_file = Path("C:/in/a/b/file.doc")
    assert map_dest_path_for_source(source_root, dest_root, source_file, ".docx") == Path("D:/out/a/b/file.docx")
```

**Step 2: Run test to verify it fails**

Run: `pytest -q`
Expected: FAIL (function missing).

**Step 3: Write minimal implementation**
```python
from __future__ import annotations

from pathlib import Path

def map_dest_path_for_source(source_root: Path, dest_root: Path, source_file: Path, dest_suffix: str) -> Path:
    relative = source_file.relative_to(source_root)
    return (dest_root / relative).with_suffix(dest_suffix)
```

**Step 4: Run test to verify it passes**

Run: `pytest -q`
Expected: PASS.

**Step 5: Compile check**

Run: `python -m compileall -q src`
Expected: exit 0.

---

### Task 3: Implement safe “dest path stays within dest root” guard

**Files:**
- Modify: `src/core/paths.py`
- Test: `tests/test_paths.py`

**Step 1: Write the failing test**
```python
from pathlib import Path

import pytest

from src.core.paths import ensure_within_root

def test_ensure_within_root_rejects_escape():
    root = Path("/dest")
    with pytest.raises(ValueError):
        ensure_within_root(root, Path("/dest/../evil/out.docx"))
```

**Step 2: Run test to verify it fails**

Run: `pytest -q`
Expected: FAIL (function missing).

**Step 3: Write minimal implementation**
```python
from pathlib import Path

def ensure_within_root(root: Path, path: Path) -> Path:
    root_resolved = root.resolve()
    path_resolved = path.resolve()
    if root_resolved not in [path_resolved, *path_resolved.parents]:
        raise ValueError("Destination path escapes destination root")
    return path
```

**Step 4: Run test to verify it passes**

Run: `pytest -q`
Expected: PASS.

---

### Task 4: Implement recursive scanner for `.doc` + `.docx`

**Files:**
- Create: `src/core/scan.py`
- Test: `tests/test_scan.py`

**Step 1: Write the failing test**

Use `tmp_path` to create:
- `in/a/file1.doc`
- `in/a/file2.docx`
- `in/a/ignore.txt`

Assert scan returns both `.doc` and `.docx`, sorted.

**Step 2: Run test to verify it fails**

Run: `pytest -q`
Expected: FAIL.

**Step 3: Write minimal implementation**

- Use `Path.rglob("*")`, filter by suffix lowercased in `{".doc", ".docx"}`.
- Return sorted list of `Path`s for determinism.

**Step 4: Run test to verify it passes**

Run: `pytest -q`
Expected: PASS.

---

### Task 5: Implement LibreOffice `soffice` detection

**Files:**
- Create: `src/core/libreoffice.py`
- Test: `tests/test_libreoffice_detection.py`

**Step 1: Write the failing test**

- Test that when `user_path` is provided and exists, it’s returned.
- Test that when `user_path` missing, detection can return `None` (don’t hardcode OS paths in tests).

**Step 2: Run test to verify it fails**

Run: `pytest -q`
Expected: FAIL.

**Step 3: Write minimal implementation**

- Function: `resolve_soffice_path(user_path: str | None) -> Path | None`
- Behavior:
  - If `user_path` provided, validate exists + executable.
  - Else try `shutil.which("soffice")` and common install locations per OS.
  - Return `Path` or `None`.

**Step 4: Run test to verify it passes**

Run: `pytest -q`
Expected: PASS.

---

### Task 6: Implement `.doc` → `.docx` conversion wrapper

**Files:**
- Create: `src/core/convert.py`
- Test: `tests/test_convert_smoke.py` (minimal, skip if `soffice` unavailable)

**Step 1: Write the failing test**

- If `resolve_soffice_path(None)` is `None`, `pytest.skip`.
- Else create a tiny `.doc` fixture (keep a real sample under `tests/fixtures/`), run conversion into `tmp_path`, and assert output `.docx` exists.

**Step 2: Run test to verify it fails**

Run: `pytest -q`
Expected: FAIL (until wrapper exists).

**Step 3: Write minimal implementation**

- Function: `convert_doc_to_docx(soffice_path: Path, source_doc: Path, dest_dir: Path) -> tuple[bool, str]`
- Implementation:
  - `subprocess.run([...], capture_output=True, text=True, check=False)`
  - Validate expected output exists (LibreOffice can “succeed” but not create output).
  - Return `(success, combined_log)`.

**Step 4: Run test to verify it passes**

Run: `pytest -q`
Expected: PASS on machines with LibreOffice installed.

---

### Task 7: Implement `.docx` copy helper

**Files:**
- Create: `src/core/copy.py`
- Test: `tests/test_copy.py`

**Step 1: Write the failing test**

- Create a dummy `.docx` file in `tmp_path`, copy it, assert destination exists and content matches.

**Step 2: Implement**

- Use `shutil.copy2`, ensure parent directory exists.

**Step 3: Verify**

Run: `pytest -q`
Expected: PASS.

---

### Task 8: Build “work item” model and processing loop (core, no Qt)

**Files:**
- Create: `src/core/work_items.py`
- Create: `src/core/pipeline.py`
- Test: `tests/test_pipeline_mapping.py`

**Step 1: Write failing test**

- Given a fake source tree, assert pipeline produces expected list of operations (convert `.doc`, optional copy `.docx`) with correct destination paths.

**Step 2: Implement minimal**

- `WorkItem` dataclass: `kind` (`convert`|`copy`), `source`, `dest_dir` or `dest_file`.
- `build_work_items(...)` uses scanner + mapping.

**Step 3: Verify**

Run: `pytest -q`
Expected: PASS.

---

### Task 9: Create Qt main window skeleton

**Files:**
- Create: `src/ui/main_window.py`
- Modify: `src/app.py`

**Step 1: Manual smoke test**

Run: `python -m src.app`
Expected: A window opens with empty placeholders.

**Step 2: Implement**

- Add widgets for source/dest pickers, checkbox, LibreOffice path, Start/Cancel, progress, log.

**Step 3: Compile check**

Run: `python -m compileall -q src`
Expected: exit 0.

---

### Task 10: Implement worker thread and signals

**Files:**
- Create: `src/ui/worker.py`
- Modify: `src/ui/main_window.py`

**Step 1: Implement**

- Worker emits:
  - `progress(total:int, done:int)`
  - `current_file(str)`
  - `log(str)`
  - `finished(summary:str)`
  - `failed(error:str)` (optional)
- Cancel: `request_cancel()` sets flag; check between items.

**Step 2: Manual smoke test**

- Start with a tiny folder; verify UI stays responsive and log updates.

---

### Task 11: Wire core pipeline into worker

**Files:**
- Modify: `src/ui/worker.py`
- Modify: `src/core/pipeline.py`

**Step 1: Implement**

- Worker calls:
  - build work items
  - for each item: convert/copy
  - overwrite policy always
  - per-item try/except, continue on error

**Step 2: Manual validation**

- Folder with `.doc` + `.docx` in nested dirs, checkbox on/off.
- Verify output tree and overwrite behavior.

---

### Task 12: Add “LibreOffice not found” UX guard

**Files:**
- Modify: `src/ui/main_window.py`
- Modify: `src/core/libreoffice.py`

**Step 1: Implement**

- Disable Start and show message if `soffice` path unresolved.
- Allow Browse to set and re-validate.

**Step 2: Manual check**

- Simulate missing LO by clearing path; confirm Start disabled.

---

### Task 13: Add summary report and counts

**Files:**
- Modify: `src/core/pipeline.py`
- Modify: `src/ui/worker.py`
- Modify: `src/ui/main_window.py`

**Step 1: Implement**

- Count: scanned docs/docx, converted, copied, failed, canceled, duration.
- Show summary in UI and log.

---

### Task 14: Packaging baseline (PyInstaller) + docs

**Files:**
- Create: `README.md`
- Create: `docs/deployment-guide.md`
- Create/Modify: `pyinstaller.spec` (or document command)

**Step 1: Document**

- Windows build steps
- macOS build steps
- LibreOffice prerequisite + how to locate `soffice`

**Step 2: Manual check**

- Build locally on one OS; confirm app starts.

---

## Execution Handoff

Plan saved to `docs/plans/2026-03-23-batch-doc-to-docx-qt-gui-implementation-plan.md`.

Two execution options:
1. Subagent-Driven (this session) — dispatch per task, review between tasks
2. Parallel Session (separate) — implement with `superpowers:executing-plans` in a new session/worktree

## Unresolved Questions

- Do you want a CLI mode too (same core pipeline, no Qt), or strictly GUI-only for v1?

