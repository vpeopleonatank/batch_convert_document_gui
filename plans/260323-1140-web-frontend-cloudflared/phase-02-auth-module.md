# Phase 02 — Auth Module

## Context Links
- [Plan overview](plan.md)
- [Phase 01](phase-01-project-setup.md)

## Overview
- **Priority:** P1 (blocking for Phase 04)
- **Status:** Pending
- **Review:** Not started
- **Description:** Simple password auth — env var password, HMAC token in httpOnly cookie

## Key Insights
- Stateless: no DB or session store needed
- HMAC token = `hmac(secret_key, "authenticated")` — all valid tokens are identical, no per-user state
- `CONVERT_WEB_PASSWORD` env var required at startup; fail fast if missing
- Cookie-based auth works transparently with cloudflared tunnel

## Requirements
- **Functional:**
  - `POST /api/login` accepts JSON `{"password": "..."}`, sets httpOnly cookie if correct
  - Dependency function `require_auth(request)` validates cookie on protected routes
  - Raise 401 if invalid/missing token
- **Non-functional:**
  - Constant-time password comparison (`hmac.compare_digest`)
  - httpOnly + SameSite=Lax cookie (no JS access)

## Architecture
```
POST /api/login
  → verify password (constant-time compare)
  → generate HMAC token using SECRET_KEY
  → set httpOnly cookie "session_token"
  → return {"ok": true}

Protected routes:
  → read "session_token" cookie
  → verify HMAC matches expected value
  → raise 401 if invalid
```

## Related Code Files
- **Create:** `src/web/auth.py`

## Implementation Steps

1. Create `src/web/auth.py`:
   - `SECRET_KEY`: generated via `secrets.token_hex(32)` at module load (per-process)
   - `EXPECTED_TOKEN`: `hmac.new(SECRET_KEY, b"authenticated", "sha256").hexdigest()`
   - `get_password() -> str`: read `CONVERT_WEB_PASSWORD` env var, raise if empty
   - `verify_password(candidate: str) -> bool`: constant-time compare with env var
   - `create_token() -> str`: return `EXPECTED_TOKEN`
   - `verify_token(token: str) -> bool`: constant-time compare with `EXPECTED_TOKEN`
   - `require_auth(request: Request) -> None`: FastAPI dependency — read cookie, verify, raise HTTPException(401) if bad
   - `set_auth_cookie(response: Response, token: str)`: set httpOnly cookie

2. Validate `CONVERT_WEB_PASSWORD` is set at import time or provide a startup check function

## Todo List
- [ ] Create src/web/auth.py
- [ ] Implement password verification (constant-time)
- [ ] Implement HMAC token generation/verification
- [ ] Implement cookie-based auth dependency
- [ ] Implement startup validation for env var

## Success Criteria
- `verify_password` uses constant-time comparison
- Cookie is httpOnly + SameSite=Lax
- Missing env var raises clear error at startup
- 401 returned for missing/invalid tokens

## Risk Assessment
- **Medium:** User forgets to set env var → clear error message at startup
- **Low:** Token replay — acceptable for this use case (single-user, tunnel-scoped)

## Security Considerations
- Constant-time comparison prevents timing attacks
- httpOnly cookie prevents XSS token theft
- SECRET_KEY regenerated per process — tokens invalidated on restart
- No password stored, only compared at login time

## Next Steps
- Phase 03: Job Manager
