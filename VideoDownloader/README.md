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

## Downloader worker

1. Copy `VideoDownloader/video_downloader.yaml.example` to `VideoDownloader/video_downloader.yaml` and edit output paths.
2. Start worker manually (optional; proxy can auto-start it):
   ```powershell
   .\.venv\Scripts\python.exe .\VideoDownloader\downloader\service.py --config .\VideoDownloader\video_downloader.yaml
   ```

The worker listens on a Windows named pipe (`ipc_pipe_name`).
Expected payload is either `DownloadRequest` directly or `{ "job": <DownloadRequest> }`.

## Notes

- Proxy forwards to downloader via named pipe and auto-starts downloader if not running.
- All downloads go into `default_output_dir`.
- Built-in supported sites are YouTube, Reddit, RedGIF, XVideo, and Streamtape.
- You can add extra sites (domain or full URL patterns) via `extra_supported_domains_or_urls` in `video_downloader.yaml`.