# Plan — Windows bundling + installer (PySide6)

Goal: ship a Windows build users can run (portable folder/zip, and optionally an installer) for this Qt GUI.

Status: MOSTLY COMPLETE (portable zip + CI done; installer/signing optional pending)

Context links:
- Existing packaging notes: `docs/deployment-guide.md`
- Prior plan phase: `plans/20260323-1114-batch-doc-to-docx-qt-gui/phase-04-packaging-and-docs.md`

Decisions (locked):
- Artifact: portable folder build zipped for distribution (`dist/batch-doc-to-docx-gui-windows-x64.zip`)
- Target: Windows 10/11 **x64** (no arm64)
- Icon: default (no custom `.ico` yet)
- Builds: supported both **manual local** and **GitHub Actions** (tag + workflow_dispatch)
- LibreOffice bundling: supported (optional) via MSI path/URL; CI uses repo var `LIBREOFFICE_MSI_URL`

Phases:
1) Phase 01 — define Windows targets (COMPLETE) → `phase-01-define-windows-targets.md`
2) Phase 02 — PyInstaller spec + build script (COMPLETE) → `phase-02-pyinstaller-spec-and-build-script.md`
3) Phase 03 — installer + signing (OPTIONAL, PENDING) → `phase-03-installer-and-code-signing.md`
4) Phase 04 — CI build artifacts (OPTIONAL, COMPLETE) → `phase-04-ci-build-and-release-artifacts.md`

Key dependencies:
- Windows environment for building (local Windows machine or GitHub Actions `windows-latest`)
- LibreOffice is runtime dependency (not bundled); end user must install it

Definition of done (minimal):
- A reproducible Windows build produces either:
  - `dist/batch-doc-to-docx-gui/` folder (baseline), and
  - portable zip `dist/batch-doc-to-docx-gui-windows-x64.zip`
- App launches without console window, and can browse to `soffice.exe`
- Docs explain: prerequisites, build command(s), where outputs are, troubleshooting
