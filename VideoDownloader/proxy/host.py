#!/usr/bin/env python3
"""Native messaging proxy host for Hubo Video Downloader.

Responsibilities:
- Read native-messaging framed requests from extension.
- Ensure downloader worker is running (start if missing).
- Forward request to downloader over named pipe.
- Return downloader response back to extension.
"""

from __future__ import annotations

import json
import shutil
import struct
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from multiprocessing.connection import Client
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class ProxyConfig:
    ipc_pipe_name: str


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
    for field in ("url", "pageHtml", "pageTitle", "timestamp"):
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


def load_config(config_path: Path) -> ProxyConfig:
    raw: dict[str, Any] = {}
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

    return ProxyConfig(ipc_pipe_name=str(raw.get("ipc_pipe_name", r"\\.\pipe\hubo_video_downloader")))


def build_ack(ok: bool, status: str, message: str, request_id: str | None = None, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": ok,
        "status": status,
        "message": message,
        "requestId": request_id or str(uuid.uuid4()),
        "receivedAt": datetime.now(timezone.utc).isoformat(),
    }
    payload.update(extra)
    return payload


def send_job_to_downloader(pipe_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    with Client(address=pipe_name, family="AF_PIPE") as conn:
        conn.send_bytes(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        raw = conn.recv_bytes()
    response = json.loads(raw.decode("utf-8"))
    if not isinstance(response, dict):
        raise ValueError("Downloader returned non-object response")
    return response


def start_downloader_process(service_py_path: Path, config_path: Path, repo_root: Path) -> bool:
    if not service_py_path.exists():
        return False

    venv_python = repo_root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        return False

    detached = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
    new_group = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    create_flags = detached | new_group

    try:
        wt_path = shutil.which("wt.exe")
        if wt_path:
            subprocess.Popen(
                [
                    wt_path,
                    "-w",
                    "0",
                    "new-tab",
                    str(venv_python),
                    str(service_py_path),
                    "--config",
                    str(config_path),
                ],
                cwd=str(repo_root),
                creationflags=create_flags,
            )
        else:
            subprocess.Popen(
                [
                    "cmd.exe",
                    "/c",
                    "start",
                    "Hubo Video Downloader Worker",
                    "cmd.exe",
                    "/k",
                    str(venv_python),
                    str(service_py_path),
                    "--config",
                    str(config_path),
                ],
                cwd=str(repo_root),
                creationflags=create_flags,
            )
        return True
    except Exception:
        return False


def forward_with_autostart(
    config: ProxyConfig,
    payload: dict[str, Any],
    service_py_path: Path,
    config_path: Path,
    repo_root: Path,
) -> dict[str, Any]:
    last_error: Exception | None = None

    for _ in range(2):  # first try + one autostart cycle
        try:
            return send_job_to_downloader(config.ipc_pipe_name, payload)
        except Exception as exc:  # pylint: disable=broad-except
            last_error = exc

        started = start_downloader_process(service_py_path, config_path, repo_root)
        if not started:
            break

        for _ in range(12):  # wait up to ~6 seconds
            time.sleep(0.5)
            try:
                return send_job_to_downloader(config.ipc_pipe_name, payload)
            except Exception as exc:  # pylint: disable=broad-except
                last_error = exc

    raise ConnectionError(f"Cannot connect to downloader worker: {last_error}")


def main() -> int:
    proxy_dir = Path(__file__).resolve().parent
    video_downloader_dir = proxy_dir.parent
    repo_root = video_downloader_dir.parent

    config_path = video_downloader_dir / "video_downloader.yaml"
    config = load_config(config_path)
    service_py_path = video_downloader_dir / "downloader" / "service.py"

    while True:
        native_message = read_message()
        if native_message is None:
            return 0

        try:
            request = to_download_request(native_message)
            downstream_payload = {
                "url": request.url,
                "pageHtml": request.page_html,
                "pageTitle": request.page_title,
                "timestamp": request.timestamp,
            }

            downstream = forward_with_autostart(
                config,
                downstream_payload,
                service_py_path,
                config_path,
                repo_root,
            )
            ack = build_ack(
                ok=bool(downstream.get("ok")),
                status=str(downstream.get("status", "error")),
                message=str(downstream.get("message", "Unknown downloader response")),
                request_id=downstream.get("requestId"),
            )
        except Exception as exc:  # pylint: disable=broad-except
            ack = build_ack(False, "error", f"Can't connect to the Downloader: {exc}")

        write_message(ack)


if __name__ == "__main__":
    raise SystemExit(main())
