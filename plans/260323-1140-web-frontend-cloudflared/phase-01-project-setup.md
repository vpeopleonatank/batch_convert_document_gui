# Phase 01 — Project Setup

## Context Links
- [Plan overview](plan.md)
- [Brainstorm](reports/brainstorm-260323-1140-web-frontend-cloudflared.md)
- [pyproject.toml](/pyproject.toml)

## Overview
- **Priority:** P1 (blocking)
- **Status:** Pending
- **Review:** Not started
- **Description:** Add web optional dependencies to pyproject.toml, create `src/web/` package skeleton

## Key Insights
- Web deps are optional — existing Qt GUI unaffected
- `src/web/` is a new package alongside `src/ui/` (Qt) and `src/core/`

## Requirements
- **Functional:** pyproject.toml gains `[project.optional-dependencies] web = [...]`
- **Non-functional:** Zero impact on existing `pip install -e '.[dev]'`

## Architecture
- `src/web/__init__.py` — empty package init
- `src/web/static/` — directory for frontend assets

## Related Code Files
- **Modify:** `pyproject.toml`
- **Create:** `src/web/__init__.py`, `src/web/static/` (directory)

## Implementation Steps

1. Add to `pyproject.toml`:
   ```toml
   [project.optional-dependencies]
   web = ["fastapi>=0.110", "uvicorn[standard]>=0.29", "python-multipart>=0.0.9"]
   dev = ["pytest>=7.0"]
   ```
2. Create `src/web/__init__.py` (empty)
3. Create `src/web/static/` directory (add `.gitkeep`)
4. Run `pip install -e '.[web]'` to verify deps resolve
5. Run `python -c "import fastapi; print(fastapi.__version__)"` to confirm

## Todo List
- [ ] Update pyproject.toml with web optional deps
- [ ] Create src/web/__init__.py
- [ ] Create src/web/static/ directory
- [ ] Verify installation works

## Success Criteria
- `pip install -e '.[web]'` succeeds
- `import fastapi` works
- Existing `pytest -q` still passes

## Risk Assessment
- **Low:** Dependency conflicts with PySide6 — unlikely, different domains
- **Mitigation:** Optional deps keep web and Qt separate

## Security Considerations
- None for this phase

## Next Steps
- Phase 02: Auth Module
