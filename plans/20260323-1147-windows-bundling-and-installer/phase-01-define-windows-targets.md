# Phase 01 — Define Windows targets

## Context Links

- Existing docs: `docs/deployment-guide.md`
- App entrypoint: `src/app.py`

## Overview

Priority: High  
Status: COMPLETE  
Goal: lock down what “bundle to Windows” means (artifact types, supported OS/arch, versioning).

## Key Insights

- PySide6 packaging works best when building on Windows (don’t cross-compile from Linux).
- LibreOffice must remain external; installer/docs must make that explicit.

## Requirements

Functional:
- Decide artifact type:
  - **Portable**: folder build (`dist/<name>/`) zipped for distribution (recommended baseline)
  - **Optional**: single-file exe (`--onefile`) if requested
  - **Optional**: installer (`.exe`) via Inno Setup/NSIS
- Decide supported OS + arch:
  - Windows 10/11 x64 baseline; arm64 only if explicitly needed
- Decide where app version comes from (keep consistent with `pyproject.toml`)

Non-functional:
- Repeatable build steps (same output layout)
- No console window for GUI builds

## Decisions (Done)

- Baseline artifact: portable folder build zipped
- Target: Windows 10/11 x64 only
- Icon: default (no custom icon)
- Builds: manual local build + GitHub Actions (manual + tag)

## Architecture

No code architecture changes; packaging surface only:
- `PyInstaller` entry: `src/app.py`
- Versioning + metadata:
  - `pyproject.toml` remains source-of-truth for version
  - Windows file metadata configured via PyInstaller version resource (optional)

## Related Code Files

Modify:
- `docs/deployment-guide.md`
- `README.md`

Create:
- `plans/20260323-1147-windows-bundling-and-installer/phase-01-define-windows-targets.md` (this)

Delete:
- none

## Implementation Steps

1. Confirm desired outputs:
   - portable zip only, or portable + installer, or single-file exe.
2. Confirm Windows arch support:
   - x64 only vs x64 + arm64.
3. Confirm branding assets:
   - icon needed (`.ico`) or use default.
4. Confirm release workflow:
   - manual build vs GitHub Actions artifacts on tag.

## Todo List

- [x] Pick baseline artifact: portable folder zip
- [x] Decide on `--onefile`: out-of-scope for baseline
- [x] Decide installer scope: optional / deferred
- [x] Decide code signing: optional / deferred

## Success Criteria

- Clear, written decisions reflected in Phase 02/03/04.

## Risk Assessment

- `--onefile` can increase startup time and false positives from AV.
- Installer brings extra tooling + maintenance.

## Security Considerations

- Avoid bundling user paths or logs into artifacts.
- If signing is used, ensure cert secrets never land in repo (CI secrets only).

## Next Steps

- Phase 02 executed (spec + build script checked in).
