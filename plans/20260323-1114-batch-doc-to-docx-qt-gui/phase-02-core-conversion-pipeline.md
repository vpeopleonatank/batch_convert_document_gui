# Phase 02 — Core conversion pipeline

## Overview

Priority: High
Status: COMPLETE
Goal: implement scanning, relative path mapping, copy `.docx`, and convert `.doc` via LibreOffice headless.

## Requirements

Functional:
- Recursive scan source folder for `.doc` and `.docx` (case-insensitive)
- For each `.doc`, compute destination `.docx` path preserving relative folders
- Convert `.doc` → `.docx` via `soffice --headless`
- Optional copy `.docx` when enabled
- Overwrite destination files
- Cancel is cooperative (stop between files)

Non-functional:
- Robust error handling: continue on failure, record errors
- No GUI dependency inside `core/`

## Related Code Files

Modify:
- `src/core/scan.py`
- `src/core/libreoffice.py`
- `src/core/convert.py`
- `src/core/copy.py`

Create (tests):
- `tests/test_scan_and_mapping.py`

## Implementation Steps

1. Implement `scan_files(source_dir)` returning ordered list of work items.
2. Implement `map_dest_path(source_dir, dest_dir, source_file)` preserving relative path.
3. Implement `detect_soffice()` with common path heuristics + user-provided override support.
4. Implement `convert_doc_to_docx(soffice_path, source_doc, dest_dir)` using `subprocess.run([...], capture_output=True, text=True)`.
5. Implement `copy_docx(source_docx, dest_docx)` with `shutil.copy2` and ensured parent directory.
6. Add unit tests for scanning + mapping (pure functions).

## Todo List

- [ ] Decide deterministic processing order (path sort)
- [ ] Decide failure policy when LibreOffice returns success but output missing

## Success Criteria

- Given a folder tree, conversion + copy produce expected destination tree.

## Risk Assessment

- LibreOffice sometimes writes output with unexpected naming; must verify output path.

## Security Considerations

- Do not pass untrusted strings to shell.
- Avoid writing outside destination root (path traversal guard).

## Next Steps

- Start Phase 03.
