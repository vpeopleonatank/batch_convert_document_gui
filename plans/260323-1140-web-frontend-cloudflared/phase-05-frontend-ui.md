# Phase 05 — Frontend UI

## Context Links
- [Plan overview](plan.md)
- [Phase 04 — Server](phase-04-fastapi-server.md)
- [Brainstorm](reports/brainstorm-260323-1140-web-frontend-cloudflared.md)

## Overview
- **Priority:** P1 (user-facing)
- **Status:** Pending
- **Review:** Not started
- **Description:** Single HTML file with embedded CSS/JS. Login, drag-drop upload, progress via WebSocket, ZIP download.

## Key Insights
- No build step — single `index.html` with `<style>` and `<script>` blocks
- WebSocket URL derived from `window.location` (works with cloudflared tunnel automatically)
- Three UI states: login → upload → progress/download

## Requirements
- **Functional:**
  - Login form: password input → POST /api/login → on success show main UI
  - Upload: drag-drop zone + file input, .doc filter, multi-file
  - Upload button → POST /api/convert (FormData with files)
  - Progress: bar + percentage + scrolling log viewer
  - Cancel button during conversion
  - Download ZIP button on completion
  - Error display for failures
- **Non-functional:**
  - Responsive (mobile-friendly for remote access)
  - Clean, minimal design
  - No external CDN dependencies

## Architecture
```
index.html
├── <style> embedded CSS
├── #login-section
│   ├── password input
│   └── login button
├── #main-section (hidden until auth)
│   ├── #upload-zone (drag-drop + file input)
│   ├── upload button
│   ├── #progress-section (hidden until job starts)
│   │   ├── progress bar
│   │   ├── current file label
│   │   ├── log viewer (pre/code with auto-scroll)
│   │   ├── cancel button
│   │   └── download button (hidden until done)
│   └── #error-display
└── <script> embedded JS
    ├── login() → fetch POST /api/login
    ├── upload() → fetch POST /api/convert
    ├── connectWS(jobId) → new WebSocket(/api/ws/{jobId})
    │   ├── onmessage: update progress bar, append logs
    │   ├── send("cancel") on cancel click
    │   └── onclose: show download if completed
    └── download(jobId) → window.location = /api/download/{jobId}
```

## Related Code Files
- **Create:** `src/web/static/index.html`

## Implementation Steps

1. Create `src/web/static/index.html`
2. **HTML structure:**
   - Login section: form with password input + submit button
   - Main section: upload zone, file list, convert button
   - Progress section: progress bar div, percentage text, log pre element, cancel + download buttons
3. **CSS (embedded):**
   - CSS variables for theming (light, clean palette)
   - Drag-drop zone: dashed border, hover highlight
   - Progress bar: container + fill div with transition
   - Log viewer: monospace, dark bg, max-height with overflow-y scroll
   - Responsive: max-width container, flexible layout
   - Buttons: primary (blue), danger (red for cancel), success (green for download)
4. **JS (embedded):**
   - `login()`: POST /api/login with JSON body, on 200 hide login show main
   - `selectFiles()`: handle file input + drag-drop, filter .doc, show file list
   - `upload()`: FormData with files, POST /api/convert, get job_id, call connectWS
   - `connectWS(jobId)`:
     - URL: `${ws_protocol}//${host}/api/ws/${jobId}`
     - onmessage: parse JSON, switch on type:
       - "progress": update bar width + text
       - "log": append to log viewer, auto-scroll
       - "current_file": update label
       - "done": show download button, hide cancel
       - "failed": show error
     - Cancel button: `ws.send("cancel")`
   - `download(jobId)`: `window.location.href = /api/download/${jobId}`
   - Drag-drop: prevent default on dragover/drop, read `e.dataTransfer.files`
5. **UX details:**
   - Disable upload button while converting
   - Show file count + names before upload
   - Auto-scroll log to bottom on new entries
   - Show summary text on completion

## Todo List
- [ ] Create HTML structure (login, upload, progress sections)
- [ ] Implement embedded CSS (responsive, clean design)
- [ ] Implement login JS
- [ ] Implement file selection + drag-drop JS
- [ ] Implement upload + job creation JS
- [ ] Implement WebSocket connection + progress updates
- [ ] Implement cancel functionality
- [ ] Implement download trigger
- [ ] Test drag-drop + file picker
- [ ] Test responsive layout

## Success Criteria
- Login flow works, session persists via cookie
- Drag-drop and file picker both work for .doc selection
- Real-time progress bar + log updates via WebSocket
- Cancel stops conversion mid-way
- Download button appears and triggers ZIP download
- Works on mobile browser (responsive)

## Risk Assessment
- **Low:** WebSocket URL construction with cloudflared — use relative path, protocol detection handles wss://
- **Low:** Large file list display — truncate if >20 files, show count

## Security Considerations
- No secrets in frontend code
- Password input type=password
- Cookie set by server (httpOnly) — JS cannot read it
- WebSocket auth via cookie (sent automatically)

## Next Steps
- Phase 06: Testing & Docs
