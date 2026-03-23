---
type: brainstorm
date: 2026-03-23
slug: web-frontend-cloudflared
---

# Brainstorm: Web Frontend with Cloudflared Tunnel

## Problem Statement
Create web frontend for batch DOC→DOCX converter, serve locally via FastAPI, tunnel via cloudflared for remote access.

## Requirements
- Remote access via cloudflared tunnel
- File upload: multi-file .doc → convert → ZIP download
- Real-time progress via WebSocket
- Simple password auth
- Plain HTML/JS frontend, no build step

## Chosen Approach: Job-based Async Conversion

### Architecture
- FastAPI backend on localhost:8000
- Single index.html with vanilla JS
- WebSocket for real-time progress
- Bearer token auth from env var
- Temp dirs per job, cleanup after download/TTL

### API Endpoints
- `POST /api/login` — password → token
- `POST /api/convert` — upload .doc files → job_id
- `WS /api/ws/{job_id}` — progress stream
- `GET /api/download/{job_id}` — ZIP download
- `GET /` — static HTML UI

### New Files
- `src/web/server.py` — FastAPI app, routes, WebSocket
- `src/web/auth.py` — token auth
- `src/web/job_manager.py` — job lifecycle
- `src/web/static/index.html` — full UI

### Dependencies
- fastapi, uvicorn[standard], python-multipart

### Security
- Password from CONVERT_WEB_PASSWORD env var
- httpOnly cookie token
- File type validation (.doc only)
- Max upload size limit
- Temp cleanup after download or 1hr TTL
