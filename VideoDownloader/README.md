# VideoDownloader

This folder contains the multi-process video downloader feature.

## Layout

- `extension/` - Edge/Chrome extension (`Hubo Video Downloader`).
- `proxy/` - native messaging host (stdin/stdout JSON framing).
- `downloader/` - long-running download service area (implemented in later steps).
- `protocol.md` - how different components communicate and exchange data.

## Quick setup (Windows)

1. Load unpacked extension from `VideoDownloader/extension` in Edge/Chrome developer mode.
2. Copy the extension ID.
3. Run:
   ```powershell
   pwsh -ExecutionPolicy Bypass -File .\VideoDownloader\proxy\register_native_host.ps1 -ExtensionId <your_extension_id>
   ```
4. Click the extension action button on a page and inspect service worker logs if needed.

## Notes

- For now, proxy replies with dummy statuses only (no downloader process yet).