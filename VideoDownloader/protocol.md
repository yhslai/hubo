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
  "message": "Download job accepted by proxy dummy handler.",
  "requestId": "e2b0f8f5-0f33-47bc-acd4-4989035ca5de",
  "receivedAt": "2026-04-10T17:32:00.040Z"
}
```

```json
{
  "ok": false,
  "status": "error",
  "message": "Unknown error logged by proxy dummy handler.",
  "requestId": "8cdd3528-0b31-4275-9f04-19656cb90737",
  "receivedAt": "2026-04-10T17:32:00.040Z"
}
```

Fields:
- `ok` (boolean): success or failure.
- `status` (string): `queued` or `error`.
- `message` (string): user-facing short result message.
- `requestId` (string): UUID from proxy.
- `receivedAt` (string): ISO-8601 timestamp set by proxy.
