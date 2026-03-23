# Phase 03 — Installer + code signing (optional)

## Context Links

- Phase 02 outputs portable zip
- Windows installer tooling:
  - Inno Setup (simple, common)
  - NSIS (more flexible, more scripting)

## Overview

Priority: Medium  
Status: PENDING  
Goal: produce a user-friendly installer and (optionally) sign binaries to reduce SmartScreen warnings.

## Key Insights

- Unsigned binaries often trigger SmartScreen/AV warnings; signing helps but costs time/money.
- Installer should not bundle LibreOffice; it should link to download instructions.

## Requirements

Functional:
- Installer installs to Program Files and creates Start Menu shortcut
- Uninstaller works
- Installer messaging calls out LibreOffice requirement + common install path

Non-functional:
- Keep installer config simple and documented

## Architecture

Proposed files:
- `packaging/windows/installer.iss` (Inno Setup)
- Optional signing step in build script/CI using secrets

## Related Code Files

Modify:
- `docs/deployment-guide.md`

Create:
- `packaging/windows/installer.iss` (if Inno Setup chosen)
- `packaging/windows/README.md` (short notes for maintainers)

Delete:
- none

## Implementation Steps

1. Choose installer tech (Inno Setup recommended).
2. Write installer definition that packages `dist/<name>/` output:
   - version sourced from project version (manual bump or scripted)
3. Add optional signing hooks:
   - local signing instructions (signtool) OR CI-based signing (if cert available)
4. Update docs with “How to build installer” steps.

## Todo List

- [ ] Decide installer tool
- [ ] Decide if signing is in-scope

## Success Criteria

- Installer installs + launches app on a clean Windows VM.

## Risk Assessment

- Signing workflow complexity (cert handling, timestamping, CI secrets).

## Security Considerations

- Never commit certificates/keys.
- Prefer CI secrets + protected branches/tags for release builds.

## Next Steps

- If releases are tagged, integrate Phase 04 CI workflow.

