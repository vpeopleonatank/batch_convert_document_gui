---
title: "Web Frontend with Cloudflared Tunnel"
description: "FastAPI web server + vanilla JS UI for remote batch DOC to DOCX conversion via cloudflared"
status: pending
priority: P2
effort: 3h
branch: main
tags: [web, fastapi, cloudflared, frontend]
created: 2026-03-23
---

# Web Frontend with Cloudflared Tunnel

## Overview

Add a web interface to the existing batch DOC-to-DOCX converter. FastAPI backend reuses `src/core/pipeline.py` (callback-driven, Qt-independent). Single-page vanilla JS frontend. Password-protected. Tunneled via cloudflared for remote access.

## Key Insight

`run_pipeline()` accepts `on_log`, `on_progress`, `on_current_file`, `is_cancelled` callbacks — fully decoupled from Qt. Web layer plugs into these callbacks to stream progress over WebSocket.

## Architecture

```
Browser <--cloudflared--> FastAPI (localhost:8000)
                            ├── POST /api/login (password auth)
                            ├── POST /api/convert (upload .doc files)
                            ├── WS /api/ws/{job_id} (progress stream)
                            ├── GET /api/download/{job_id} (ZIP)
                            └── GET / (static index.html)
```

## Phases

| # | Phase | File | Status |
|---|-------|------|--------|
| 1 | Project Setup | [phase-01](phase-01-project-setup.md) | Pending |
| 2 | Auth Module | [phase-02](phase-02-auth-module.md) | Pending |
| 3 | Job Manager | [phase-03](phase-03-job-manager.md) | Pending |
| 4 | FastAPI Server | [phase-04](phase-04-fastapi-server.md) | Pending |
| 5 | Frontend UI | [phase-05](phase-05-frontend-ui.md) | Pending |
| 6 | Testing & Docs | [phase-06](phase-06-testing-and-docs.md) | Pending |

## Dependencies

- `fastapi`, `uvicorn[standard]`, `python-multipart` added as optional deps
- LibreOffice `soffice` must be available on host
- `cloudflared` installed separately for tunneling

## New Files

```
src/web/
├── __init__.py
├── auth.py          # Token auth via HMAC + httpOnly cookie
├── job-manager.py   # Job lifecycle, temp dirs, cleanup
├── server.py        # FastAPI routes + WebSocket
└── static/
    └── index.html   # Single-page UI (vanilla JS)
```

## Entry Point

```bash
pip install -e '.[web]'
CONVERT_WEB_PASSWORD=secret python -m src.web.server
```
