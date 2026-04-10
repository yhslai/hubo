# Video Downloader Message Contracts

These contracts are shared across extension, proxy, and downloader.

## DownloadRequest

```json
{
  "url": "https://example.com/video-page",
  "pageHtml": "<html>...</html>",
  "pageTitle": "Example title",
  "timestamp": "2026-04-10T17:32:00.000Z"
}
```

Fields:
- `url` (string, required): current tab URL.
- `pageHtml` (string, required): captured full HTML (`document.documentElement.outerHTML`).
- `pageTitle` (string, required): tab title.
- `timestamp` (string, required): ISO-8601 timestamp produced by extension.

## ProxyAck

```json
{
  "ok": true,
  "status": "queued",
  "message": "Download started.",
  "requestId": "e2b0f8f5-0f33-47bc-acd4-4989035ca5de",
  "receivedAt": "2026-04-10T17:32:00.040Z"
}
```

```json
{
  "ok": false,
  "status": "unsupported",
  "message": "Unsupported URL/site: https://example.com",
  "requestId": "8cdd3528-0b31-4275-9f04-19656cb90737",
  "receivedAt": "2026-04-10T17:32:00.040Z"
}
```

```json
{
  "ok": false,
  "status": "error",
  "message": "Can't connect to the Downloader: ...",
  "requestId": "b14f25fd-5091-4948-8eeb-7f7f6cc5cb8e",
  "receivedAt": "2026-04-10T17:32:00.040Z"
}
```

Fields:
- `ok` (boolean): success or failure.
- `status` (string): `queued`, `unsupported`, or `error`.
- `message` (string): user-facing short result message.
- `requestId` (string): UUID from downloader/proxy.
- `receivedAt` (string): ISO-8601 timestamp set by proxy.

Behavior:
- Proxy forwards requests to downloader over named pipe.
- If downloader is not running, proxy attempts to launch it in a separate terminal and retries.

## Downloader IPC (S2)

Worker IPC transport is Windows named pipe (`ipc_pipe_name`).

Request payload can be either the `DownloadRequest` directly, or wrapped:

```json
{
  "job": {
    "url": "https://example.com/video-page",
    "pageHtml": "<html>...</html>",
    "pageTitle": "Example title",
    "timestamp": "2026-04-10T17:32:00.000Z"
  }
}
```

All downloads are written to one configured directory (`default_output_dir`), regardless of source site.

Worker response:

```json
{
  "ok": true,
  "status": "queued",
  "message": "Download job queued.",
  "requestId": "9f9ce5d4-f7d4-4cf3-8f0d-57ac8de6ebf9"
}
```
