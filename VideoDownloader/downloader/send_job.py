#!/usr/bin/env python3
"""Small helper to enqueue a downloader job to the local worker."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from multiprocessing.connection import Client


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send one download job to local worker")
    parser.add_argument("url", help="Page URL")
    parser.add_argument("--title", default="", help="Page title")
    parser.add_argument("--html", default="", help="Page HTML")
    parser.add_argument("--pipe", default=r"\\.\pipe\hubo_video_downloader", help="Windows named pipe")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = {
        "url": args.url,
        "pageHtml": args.html,
        "pageTitle": args.title,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    with Client(address=args.pipe, family="AF_PIPE") as conn:
        conn.send_bytes(json.dumps(payload).encode("utf-8"))
        data = conn.recv_bytes()

    print(data.decode("utf-8").strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
