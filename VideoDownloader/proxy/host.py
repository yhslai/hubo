#!/usr/bin/env python3
"""Dummy native messaging host for Hubo Video Downloader.

S1 scope:
- Parse native messaging protocol from stdin.
- Accept extension payload and validate required fields.
- Return a random dummy ack (queued or error).
"""

import json
import random
import struct
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class DownloadRequest:
    url: str
    page_html: str
    page_title: str
    timestamp: str


def read_message() -> dict[str, Any] | None:
    header = sys.stdin.buffer.read(4)
    if not header:
        return None

    if len(header) != 4:
        raise ValueError("Invalid native messaging header size")

    (message_length,) = struct.unpack("=I", header)
    payload = sys.stdin.buffer.read(message_length)
    if len(payload) != message_length:
        raise ValueError("Incomplete native messaging payload")

    return json.loads(payload.decode("utf-8"))


def write_message(data: dict[str, Any]) -> None:
    encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("=I", len(encoded)))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


def to_download_request(payload: dict[str, Any]) -> DownloadRequest:
    required = ["url", "pageHtml", "pageTitle", "timestamp"]
    for field in required:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(payload[field], str):
            raise ValueError(f"Field {field} must be a string")

    return DownloadRequest(
        url=payload["url"],
        page_html=payload["pageHtml"],
        page_title=payload["pageTitle"],
        timestamp=payload["timestamp"],
    )


def build_dummy_ack() -> dict[str, Any]:
    success = random.choice([True, False])
    return {
        "ok": success,
        "status": "queued" if success else "error",
        "message": (
            "Download started (dummy proxy response)."
            if success
            else "Unknown error logged by proxy dummy handler."
        ),
        "requestId": str(uuid.uuid4()),
        "receivedAt": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    while True:
        message = read_message()
        if message is None:
            return 0

        try:
            _request = to_download_request(message)
            ack = build_dummy_ack()
        except Exception as exc:  # pylint: disable=broad-except
            ack = {
                "ok": False,
                "status": "error",
                "message": f"Invalid request: {exc}",
                "requestId": str(uuid.uuid4()),
                "receivedAt": datetime.now(timezone.utc).isoformat(),
            }

        write_message(ack)


if __name__ == "__main__":
    raise SystemExit(main())