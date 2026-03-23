# Phase 03 — Qt GUI + worker thread

## Overview

Priority: High
Status: COMPLETE
Goal: build a responsive GUI that runs conversion work off the UI thread and streams progress/logs.

## Requirements

- Folder pickers for source/destination
- Checkbox for “Copy existing .docx”
- LibreOffice path auto-detect + browse override
- Start/Cancel controls
- Progress: bar + current file
- Log panel + summary dialog/text

## Related Code Files

Modify/Create:
- `src/ui/main_window.py`
- `src/ui/worker.py`
- `src/app.py`

## Implementation Steps

1. Build `MainWindow` with inputs and validation (disable Start until valid).
2. Implement a `Worker` (QObject in a QThread) that:
   - emits `progress(total, done)`, `current_file(path)`, `log(line)`, `finished(summary)`
   - checks a cancel flag between items
3. Wire Cancel to set cancel flag + disable itself.
4. Ensure exceptions are caught and reported via log.

## Todo List

- [ ] Decide how to store persistent settings (QSettings) (optional)

## Success Criteria

- UI stays responsive during large conversions.
- Cancel stops future work.

## Risk Assessment

- Threading mistakes can crash; keep Qt signal/slot boundaries clean.

## Security Considerations

- Do not allow running arbitrary executables beyond selected `soffice` path.

## Next Steps

- Start Phase 04.
