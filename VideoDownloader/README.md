# VideoDownloader

This folder contains the multi-process video downloader feature.

## Layout

- `extension/` - Edge/Chrome extension (`Hubo Video Downloader`).
- `proxy/` - native messaging host (stdin/stdout JSON framing).
- `downloader/` - long-running download service area.
- `protocol.md` - how different components communicate and exchange data.

## Quick setup (Windows)

1. Load unpacked extension from `VideoDownloader/extension` in Edge/Chrome developer mode.
2. Copy the extension ID.
3. Run:
   ```powershell
   pwsh -ExecutionPolicy Bypass -File .\VideoDownloader\proxy\register_native_host.ps1 -ExtensionId <your_extension_id>
   ```
4. Click the extension action button on a page and inspect service worker logs if needed.

## Downloader worker (S2)

1. Copy `VideoDownloader/video_downloader.yaml.example` to `VideoDownloader/video_downloader.yaml` and edit output paths.
2. Start worker:
   ```powershell
   .\VideoDownloader\downloader\run_downloader.cmd
   ```

The worker listens on a Windows named pipe (`ipc_pipe_name`).
Expected payload is either `DownloadRequest` directly or `{ "job": <DownloadRequest> }`.

## Notes

- Proxy now forwards to downloader via named pipe and auto-starts downloader if not running (launches `VideoDownloader/downloader/service.py` directly, preferring `./.venv/Scripts/python.exe`).
- Extension action shows an intermediate waiting state (`...`) before final ack.
- Downloader shows a clickable Windows toast when a download finishes (opens Explorer with the file selected, requires `win11toast`).
- Downloader logs progress every 10% (`job.progress`) with requestId, current file path, and speed.
- Downloader routing:
  - `python -m yt_dlp` for youtube/reddit/redgif/pornhub/xvideo (and unknown sites)
  - streamtape fallback using `tools/streamtape_cli.py` then `python -m yt_dlp`
- All downloads go into one single directory: `default_output_dir`.
- Remember that we use uv/venv, so all Python calling should precede with `.\.venv\Scripts\python.exe`.