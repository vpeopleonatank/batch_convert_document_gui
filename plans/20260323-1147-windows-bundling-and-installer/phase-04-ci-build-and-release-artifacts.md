# Phase 04 — CI build + release artifacts (optional)

## Context Links

- Phase 02 build script produces portable artifact
- Workflow implemented: `.github/workflows/build-windows.yml`

## Overview

Priority: Medium  
Status: COMPLETE  
Goal: build Windows artifacts in GitHub Actions for repeatability and easy downloads.

## Key Insights

- CI avoids “need a Windows box” for every build, but still uses Windows runners.
- For PyInstaller, cache pip downloads to speed up builds.

## Requirements

Functional:
- On tag push (e.g. `v0.1.0`), produce and upload:
  - `dist/batch-doc-to-docx-gui-windows-x64.zip`
  - optional installer artifact
- Provide manual workflow dispatch for ad-hoc builds

Non-functional:
- Keep workflow readable and minimal

## Architecture

Workflow:
- `.github/workflows/build-windows.yml`

Jobs:
- checkout
- setup Python
- install deps
- run `scripts/build-windows.ps1`
- upload artifact

## Related Code Files

Created:
- `.github/workflows/build-windows.yml`

Modify:
- `docs/deployment-guide.md`

Delete:
- none

## Implementation Steps

1. Add `build-windows.yml` with:
   - `on: workflow_dispatch` and `on: push: tags: [ "v*" ]`
   - `runs-on: windows-latest`
2. Run PowerShell build script.
3. Upload artifact(s).
4. (Optional) publish GitHub Release on tag.

## Todo List

- [x] Release strategy: artifacts only (no auto GitHub Release publish)

## Success Criteria

- A tag push builds and uploads artifacts successfully.

## Risk Assessment

- Runner changes can break builds; pin Python minor version.

## Security Considerations

- If signing is enabled, restrict it to tags and use GitHub Environments for approvals.
