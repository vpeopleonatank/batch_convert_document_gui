# Phase 04 — FastAPI Server

## Context Links
- [Plan overview](plan.md)
- [Phase 02 — Auth](phase-02-auth-module.md)
- [Phase 03 — Job Manager](phase-03-job-manager.md)
- [libreoffice.py](/src/core/libreoffice.py) — `resolve_soffice_path()`

## Overview
- **Priority:** P1 (core)
- **Status:** Pending
- **Review:** Not started
- **Description:** FastAPI app with routes for login, upload, WebSocket progress, ZIP download. Serves static frontend.

## Key Insights
- `resolve_soffice_path(None)` auto-detects soffice — call at startup, fail fast if not found
- WebSocket reads from `job.message_queue` (asyncio.Queue) — clean async/thread bridge
- Static files served via `StaticFiles` mount at `/static` or inline via `FileResponse` for index.html
- `BackgroundTasks` or `asyncio.create_task` for stale job cleanup loop

## Requirements
- **Functional:**
  - `GET /` → serve index.html
  - `POST /api/login` → verify password, set cookie, return JSON
  - `POST /api/convert` → accept multipart .doc files, create job, save files, start conversion, return job_id
  - `WS /api/ws/{job_id}` → stream progress JSON, accept "cancel" command
  - `GET /api/download/{job_id}` → serve ZIP, trigger cleanup
- **Non-functional:**
  - Max upload size: 50MB total (configurable via env)
  - File extension validation: only `.doc` accepted
  - Startup: auto-detect soffice, validate password env var
  - Background task: cleanup stale jobs every 5 minutes

## Architecture
```
FastAPI app
├── Lifespan:
│   ├── startup: resolve soffice, validate env, init JobManager
│   └── shutdown: cleanup all jobs
├── Routes:
│   ├── GET / → FileResponse(static/index.html)
│   ├── POST /api/login → auth.verify_password → set cookie
│   ├── POST /api/convert [auth required]
│   │   ├── validate file extensions
│   │   ├── job = manager.create_job()
│   │   ├── save uploaded files to job.input_dir
│   │   ├── manager.run_job(job.id)
│   │   └── return {"job_id": job.id}
│   ├── WS /api/ws/{job_id} [auth via cookie]
│   │   ├── loop: msg = await job.message_queue.get()
│   │   ├── send JSON to client
│   │   ├── accept "cancel" text from client → manager.cancel_job
│   │   └── break on "done" or "failed" message
│   └── GET /api/download/{job_id} [auth required]
│       ├── zip_path = manager.zip_output(job_id)
│       └── return FileResponse(zip_path)
└── Background: cleanup_stale every 5min via asyncio loop
```

## Related Code Files
- **Create:** `src/web/server.py`
- **Read:** `src/web/auth.py`, `src/web/job-manager.py`, `src/core/libreoffice.py`

## Implementation Steps

1. Create `src/web/server.py`
2. Define lifespan context manager:
   - `soffice_path = resolve_soffice_path(None)` — raise if None
   - Read `CONVERT_WEB_PASSWORD` — raise if empty
   - Init `JobManager(soffice_path)`
   - Store on `app.state`
   - Start cleanup background task
3. Mount static files: `app.mount("/static", StaticFiles(directory=...), name="static")`
4. Implement routes:
   - `GET /` → `FileResponse(static/index.html)`
   - `POST /api/login` → JSON body `{"password": "..."}`, verify, set cookie, return `{"ok": true}`
   - `POST /api/convert` → `Depends(require_auth)`, accept `UploadFile` list, validate `.doc` extension, save to temp, run job
   - `WS /api/ws/{job_id}` → verify auth cookie manually (WebSocket has no Depends for cookies easily), loop on queue
   - `GET /api/download/{job_id}` → `Depends(require_auth)`, zip + return file
5. Add `if __name__ == "__main__"` or `__main__.py` entry:
   ```python
   uvicorn.run("src.web.server:app", host="0.0.0.0", port=8000)
   ```
6. Add cleanup background task:
   ```python
   async def periodic_cleanup():
       while True:
           await asyncio.sleep(300)
           manager.cleanup_stale()
   ```

## Todo List
- [ ] Create src/web/server.py
- [ ] Implement lifespan (soffice detection, env validation, JobManager init)
- [ ] Implement GET / route
- [ ] Implement POST /api/login route
- [ ] Implement POST /api/convert route with file validation
- [ ] Implement WS /api/ws/{job_id} with queue consumption
- [ ] Implement GET /api/download/{job_id}
- [ ] Add periodic cleanup background task
- [ ] Add __main__.py or if __name__ block for uvicorn

## Success Criteria
- Server starts, detects soffice, validates password env
- Login sets httpOnly cookie
- Upload accepts only .doc files, returns job_id
- WebSocket streams progress in real-time
- Download returns valid ZIP with .docx files
- Stale jobs cleaned automatically

## Risk Assessment
- **Medium:** WebSocket auth — can't use `Depends` directly; must read cookie from WebSocket headers manually
  - Mitigation: parse `request.cookies` in WS endpoint
- **Low:** Large file uploads — 50MB default limit adequate for .doc files

## Security Considerations
- Auth required on all endpoints except `GET /` and `POST /api/login`
- File extension whitelist (.doc only) prevents arbitrary uploads
- Max upload size prevents disk exhaustion
- Job IDs are UUIDs — unguessable
- Cleanup prevents orphaned temp files

## Next Steps
- Phase 05: Frontend UI
