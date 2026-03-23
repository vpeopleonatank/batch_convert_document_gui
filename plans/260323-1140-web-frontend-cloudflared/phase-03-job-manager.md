# Phase 03 — Job Manager

## Context Links
- [Plan overview](plan.md)
- [pipeline.py](/src/core/pipeline.py) — `run_pipeline()` with callbacks
- [work_items.py](/src/core/work_items.py) — WorkItem dataclass
- [libreoffice.py](/src/core/libreoffice.py) — `resolve_soffice_path()`

## Overview
- **Priority:** P1 (blocking for Phase 04)
- **Status:** Pending
- **Review:** Not started
- **Description:** Manages job lifecycle: create temp dirs, run pipeline in background thread, track progress, create ZIP, cleanup

## Key Insights
- `run_pipeline()` is synchronous + callback-driven → run in `threading.Thread`
- Job state must be thread-safe — use `threading.Lock` on jobs dict
- Progress updates go into job state; WebSocket handler reads from there
- Use `asyncio.Queue` per job for WebSocket message passing (thread → async bridge)
- TTL-based auto-cleanup prevents disk bloat

## Requirements
- **Functional:**
  - `create_job()` → UUID job_id, temp input/output dirs
  - `run_job(job_id, soffice_path)` → start pipeline in thread, update job state via callbacks
  - `get_job(job_id)` → current state (status, progress, logs)
  - `cancel_job(job_id)` → set cancel flag, pipeline checks `is_cancelled`
  - `zip_output(job_id)` → create ZIP of output dir, return path
  - `cleanup_job(job_id)` → delete temp dirs
- **Non-functional:**
  - Thread-safe state updates
  - Auto-cleanup jobs older than 1hr via background task
  - Max concurrent jobs limit (default: 2)

## Architecture
```
Job dataclass:
  id: str (UUID)
  status: "pending" | "running" | "completed" | "failed" | "cancelled"
  input_dir: Path (tempdir)
  output_dir: Path (tempdir)
  progress_total: int
  progress_done: int
  logs: list[str]
  message_queue: asyncio.Queue  # thread→WS bridge
  cancel_flag: threading.Event
  created_at: float

JobManager:
  _jobs: dict[str, Job]       # protected by _lock
  _lock: threading.Lock
  _soffice_path: Path
  _max_concurrent: int
```

### Thread-to-async bridge
- Pipeline callbacks call `queue.put_nowait({"type": "progress", ...})`
- WebSocket handler does `await queue.get()` in async loop
- On completion, callback puts `{"type": "done", "summary": ...}`

## Related Code Files
- **Create:** `src/web/job-manager.py`
- **Read:** `src/core/pipeline.py`, `src/core/libreoffice.py`

## Implementation Steps

1. Create `src/web/job-manager.py`
2. Define `Job` dataclass with fields above
3. Implement `JobManager` class:
   - `__init__(soffice_path, max_concurrent=2)`
   - `create_job() -> Job`: make temp dirs via `tempfile.mkdtemp()`, store job
   - `run_job(job_id)`: validate job exists, check concurrent limit, start thread
   - Thread target: call `run_pipeline()` with callbacks that:
     - `on_log(line)` → append to `job.logs`, put to `job.message_queue`
     - `on_progress(total, done)` → update `job.progress_*`, put to queue
     - `on_current_file(name)` → put to queue
     - `is_cancelled()` → return `job.cancel_flag.is_set()`
   - On completion: set `job.status = "completed"`, put done message
   - On exception: set `job.status = "failed"`, log error
   - `cancel_job(job_id)`: set cancel_flag
   - `get_job(job_id) -> Job | None`
   - `zip_output(job_id) -> Path`: create ZIP from output_dir using `shutil.make_archive`
   - `cleanup_job(job_id)`: delete temp dirs, remove from dict
   - `cleanup_stale(ttl_seconds=3600)`: remove jobs older than TTL

4. Note: `copy_existing_docx=False` for web (only .doc conversion makes sense for upload scenario)

## Todo List
- [ ] Create Job dataclass
- [ ] Implement JobManager.create_job
- [ ] Implement JobManager.run_job with threading
- [ ] Implement pipeline callback → asyncio.Queue bridge
- [ ] Implement cancel_job
- [ ] Implement zip_output
- [ ] Implement cleanup_job and cleanup_stale
- [ ] Add max concurrent jobs check

## Success Criteria
- Pipeline runs in background thread without blocking event loop
- Progress updates flow from thread to async Queue
- Cancel flag stops pipeline between files
- ZIP output contains converted .docx files
- Stale jobs cleaned up automatically

## Risk Assessment
- **Medium:** LibreOffice subprocess hangs → no per-file timeout in current `convert.py`
  - Mitigation: acceptable for v1; document as known limitation
- **Low:** Temp dir cleanup fails if files locked → use `shutil.rmtree(ignore_errors=True)`

## Security Considerations
- Temp dirs created with restrictive permissions (default `tempfile.mkdtemp`)
- Job IDs are UUIDs — not guessable
- Max concurrent jobs prevents resource exhaustion

## Next Steps
- Phase 04: FastAPI Server (consumes JobManager)
