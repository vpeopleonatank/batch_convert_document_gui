# Phase 04 — Packaging + docs

## Overview

Priority: Medium
Status: COMPLETE
Goal: make a repeatable build for Windows/macOS and document prerequisites.

## Requirements

- Packaging tool: PyInstaller (baseline)
- Document how to install/find LibreOffice on each OS
- Document expected command line and troubleshooting tips

## Related Files

Create/Modify:
- `README.md`
- `docs/deployment-guide.md`

## Implementation Steps

1. Add PyInstaller spec (or documented command) for building.
2. Add runtime LibreOffice detection strategy docs.
3. Add “Known issues” (fonts, locked files, LO first-run prompts).

## Todo List

- [ ] Decide whether to bundle LibreOffice (likely out-of-scope for v1)

## Success Criteria

- A teammate can build installers on Windows/macOS following docs.

## Risk Assessment

- Packaging Qt apps differs by OS; document exact steps.

## Security Considerations

- Avoid bundling sensitive paths/config.
