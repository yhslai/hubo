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


## S2: Build downloader (standalone process)

- Implement a Python downloader service process with a simple IPC server (named pipe abstraction).
- Downloader should read config from `video_downloader.yaml`, then:
	- Waiting for download jobs from Proxy
	- Use proper tool depending on the site:
		- `yt-dlp` for Youtube
		- extract video download url from `tools/streamtape.cli.py` then download
	- The actual downloading should happen in a separate subprocess so it's not blocking


## S3: Wire All Components

- The Proxy should find the existing running Downloader, and if none, starts a new one in a new Windows Terminal console
- The Proxy should return to the Extension about the Downloader's state:
	- If it cannot find a running Downloader and can't start one, then error saying can't connect to the Downloader
	- If it successful send a job to the Downloader, then shows what Downloader reports (unsupported url, download started, or other errors)
	- Since the Downloader might take seconds to parse the web page etc, the Extension icon/message should have an intermediate 'waiting response' state
	- No need to show Download Finished on the extension. Download job is fire and forget from the extension's perspective (unless the download can't even start)
- When the download is finished, Downloader should show system notification, and the notification should be clickable and jump to the download destination folder, the file downloaded selected (there might be a python package can handle that? Survey first)


## S4: Show download progress

The Downloader should show download progress (the file path, request id, download speed and a updating progress bar). To keep it simple, we just write a new log line every 10% of progress (0% included, but only start logging progress when the download actually started and there are bytes flowing in to avoid misleading), instead of making a self-cleaning TUI.

# Done Notes

Implemented a full `VideoDownloader/` workflow with extension + native host proxy + standalone downloader service:

- Added Edge/Chrome extension (`VideoDownloader/extension`) with toolbar-click capture of `{url, pageHtml, pageTitle, timestamp}`, native-message send, and badge feedback states (`...`, `OK`, `ERR`).
- Implemented Python native messaging proxy (`VideoDownloader/proxy/host.py`) with Chrome framing I/O, request validation, named-pipe forwarding, and downloader auto-start (Windows Terminal / cmd fallback) when worker is not running.
- Added native host setup artifacts (`native-messaging-host.template.json`, `native-messaging-host.json`, `proxy_host.cmd`, `register_native_host.ps1`) and a single feature README.
- Implemented long-running downloader worker (`VideoDownloader/downloader/service.py`) using Windows named pipe IPC, background job threads, site detection, and queue acknowledgements.
- Added download execution via `yt-dlp` for supported domains (YouTube, Reddit, Redgif, Pornhub, Xvideo) plus Streamtape direct-link extraction through `tools/streamtape_cli.py`.
- Added YAML config template + local config (`video_downloader.yaml.example`, `video_downloader.yaml`) for output directory and pipe name.
- Implemented progress logging every 10% with speed-aware filtering, plus completion toast notifications (click opens Explorer with downloaded file selected).