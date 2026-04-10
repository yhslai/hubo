Make a video downloader for various sites. We'd like to support:

- Youtube (via `yt-dlp`)
- Streamtape (see `tools/streamtape_cli.py`)
- Reddit
- Redgif
- Pornhub
- Xvideo

Since we'd like to let the user to simply click a button on the browser (assuming Edge) to trigger downloading, the project needs several parts:

1. A Chrome extension (Edge compatible), "Hubo Video Downloader"
2. A proxy executive to receive the extension's native message (see [Native messaging  |  Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging))
3. An actual downloader

Upon receiving a message from the Extension (the URL and the whole HTML page), the Proxy will pass it to the Downloader (via IPC). The Downloader will decide how to download it and where to store the file (need to be configurable in a yaml file, and the yaml file should be gitignored but has an .example template file committed). If the Downloader process is not running, the Proxy has to launch one (but as a standalone process that can be closed independently and with a console window, so the downloading won't be interrupted if the Proxy is terminated.)

# Implementation Plan

## S1: Define protocol, config, and folder layout

- Add a dedicated area for this feature (`${rootPath}/VideoDownloader/`, not in `tools` as `tools` is more simple one-shot tools.) with three parts:
  - `extension/` (Edge/Chrome extension)
  - `proxy/` (native messaging host)
  - `downloader/` (long-running download job management process)
- Define JSON message contracts shared by extension/proxy/downloader:
  - Request: `{ url, pageHtml, pageTitle, timestamp }`
  - Response/ack shape from proxy for success/failure feedback.
  
Then:

- Create Manifest V3 extension "Hubo Video Downloader" with:
  - Action button (toolbar click triggers capture/send).
  - Permissions for active tab + native messaging.
- On click:
  - Capture current tab URL/title and page HTML (content script or scripting API).
  - Send payload to native host and show user feedback (queued/failed).
- Keep extension minimal (no heavy parsing in browser).

- Implement native messaging host in Python that:
  - Reads Chrome native messaging stdin framing.
- Keep proxy lightweight and stateless so each browser invocation is fast.
- Add Windows setup script to register native messaging host manifest for Edge/Chrome.

At this step we don't actually make downloader yet. Just ensure that the message can be passed between the Extension and the Proxy (the Proxy just needs to randomly respond download started or an unknown error logged message as dummy tests now)

Keep it simple: don't add README.md for each components. Just one `VideoDownloader/README.md`. The Windows setup script should be super simple and add reg for both Edge and Chrome (instead of taking an argument to specify which browser). Don't add unneeded JSON schema.


## S2: Build downloader worker (standalone process)

- Implement a Python downloader service process with a simple IPC server (localhost TCP or named pipe abstraction).
- Worker behavior:
  - Accept download jobs from proxy.
  - Route by extractor strategy:
    - `yt-dlp` for YouTube + Reddit + Redgif + Pornhub + Xvideo (primary path)
    - Streamtape handler using `tools/streamtape_cli.py` fallback.
  - Resolve output path using YAML rules and sanitize filenames.
  - Run each job in background subprocess so worker remains responsive.
- Add structured logs and clear terminal output so user can keep worker console open.

## S3: Build native messaging proxy executable


## S4: Build Edge/Chrome extension UI + messaging


## S5: Integration, install scripts, and safety checks

- 
- Add dependency checks:
  - Python packages in `requirements.txt`
  - `yt-dlp` availability (or documented install path in config)
- Add basic end-to-end validation checklist:
  - Worker auto-start from proxy
  - Queueing jobs from extension repeatedly
  - Correct per-site routing and output locations
- Document known limitations and fallback behavior when a site extractor fails.

## S6: Hardening and quality pass

- Add timeout/retry and duplicate job guard (same URL within short interval).
- Improve security posture:
  - Validate native host origin/allowed extension IDs.
  - Enforce max payload size for HTML.
- Add lightweight tests for routing/config parsing/path resolution.
- Final documentation polish (installation, usage, logs, common errors).

