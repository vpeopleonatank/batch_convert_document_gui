# Phase 06 — Testing & Docs

## Context Links
- [Plan overview](plan.md)
- All previous phases

## Overview
- **Priority:** P2
- **Status:** Pending
- **Review:** Not started
- **Description:** Unit tests for auth + job manager + API routes. Update README + deployment guide with web usage.

## Key Insights
- FastAPI `TestClient` provides sync test interface including WebSocket testing
- Job manager tests can mock `run_pipeline` to avoid needing LibreOffice
- Auth tests are pure unit tests (no external deps)
- Existing tests in `tests/` must continue passing

## Requirements
- **Functional:**
  - Test auth: password verify, token create/verify, cookie flow
  - Test job manager: create, run (mocked pipeline), cancel, cleanup
  - Test API: login flow, upload validation, download
  - README updated with web usage section
  - Deployment guide updated with cloudflared instructions
- **Non-functional:**
  - Tests runnable without LibreOffice (mock convert)
  - All existing tests still pass

## Architecture
```
tests/
├── test_web_auth.py        # Auth module unit tests
├── test_web_job_manager.py  # Job manager tests (mock pipeline)
└── test_web_api.py          # FastAPI TestClient integration tests
```

## Related Code Files
- **Create:** `tests/test_web_auth.py`, `tests/test_web_job_manager.py`, `tests/test_web_api.py`
- **Modify:** `README.md`, `docs/deployment-guide.md`

## Implementation Steps

### Tests

1. **test_web_auth.py:**
   - `test_verify_password_correct` — set env, verify returns True
   - `test_verify_password_wrong` — verify returns False
   - `test_verify_password_timing` — constant-time (assert uses hmac.compare_digest)
   - `test_create_and_verify_token` — round-trip
   - `test_verify_token_invalid` — bad token returns False
   - `test_require_auth_no_cookie` — raises 401
   - `test_require_auth_bad_cookie` — raises 401
   - `test_require_auth_valid_cookie` — passes

2. **test_web_job_manager.py:**
   - `test_create_job` — dirs created, status=pending
   - `test_run_job_success` — mock pipeline, status→completed, logs populated
   - `test_run_job_cancel` — set cancel flag, status→cancelled
   - `test_zip_output` — creates valid ZIP
   - `test_cleanup_job` — temp dirs deleted, job removed
   - `test_cleanup_stale` — old jobs removed, new ones kept
   - `test_max_concurrent` — rejects when limit reached

3. **test_web_api.py:**
   - `test_login_success` — set-cookie header present
   - `test_login_wrong_password` — 401
   - `test_convert_no_auth` — 401
   - `test_convert_invalid_extension` — 400 (reject .txt)
   - `test_convert_success` — job_id returned (mock pipeline)
   - `test_download_no_auth` — 401
   - `test_root_serves_html` — 200, content-type text/html

### Docs

4. **README.md** — add "Web Interface" section:
   ```
   ## Web Interface
   pip install -e '.[web]'
   CONVERT_WEB_PASSWORD=yourpassword python -m src.web.server
   # Open http://localhost:8000
   # For remote: cloudflared tunnel --url http://localhost:8000
   ```

5. **docs/deployment-guide.md** — add web deployment section:
   - Environment variables: `CONVERT_WEB_PASSWORD` (required)
   - Running: uvicorn command
   - Cloudflared: install, tunnel command, persistent tunnel config
   - Security notes: always use cloudflared (not expose port directly), change password

## Todo List
- [ ] Create tests/test_web_auth.py
- [ ] Create tests/test_web_job_manager.py
- [ ] Create tests/test_web_api.py
- [ ] Run all tests (existing + new)
- [ ] Update README.md with web usage
- [ ] Update docs/deployment-guide.md with cloudflared setup
- [ ] Verify existing tests unaffected

## Success Criteria
- All new tests pass
- All existing tests still pass
- `pytest -q` exits 0
- README has clear web setup instructions
- Deployment guide covers cloudflared tunnel

## Risk Assessment
- **Low:** Test isolation — mock pipeline to avoid LibreOffice dependency in CI
- **Low:** TestClient WebSocket — FastAPI supports it but requires careful async handling

## Security Considerations
- Tests must not hardcode real passwords (use test fixtures)
- Test env vars cleaned up via monkeypatch

## Next Steps
- Deploy and test with cloudflared tunnel end-to-end
