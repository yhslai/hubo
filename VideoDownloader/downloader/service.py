#!/usr/bin/env python3
"""Video downloader worker service.

- Long-running Windows named-pipe server.
- Accepts download jobs as JSON payloads.
- Routes jobs to extractor strategies.
- Executes downloads in background job threads.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from dataclasses import dataclass
from multiprocessing.connection import Listener
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

LOGGER = logging.getLogger("video_downloader.worker")

SUPPORTED_SITES = {"youtube", "reddit", "redgif", "pornhub", "xvideo", "streamtape"}


@dataclass(slots=True)
class WorkerConfig:
    default_output_dir: Path
    ipc_pipe_name: str


@dataclass(slots=True)
class DownloadJob:
    request_id: str
    url: str
    page_html: str
    page_title: str
    timestamp: str


def log_event(event: str, **fields: Any) -> None:
    LOGGER.info(json.dumps({"event": event, **fields}, ensure_ascii=False))


def load_config(config_path: Path) -> WorkerConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    return WorkerConfig(
        default_output_dir=Path(raw.get("default_output_dir") or raw.get("download_dir") or "./downloads"),
        ipc_pipe_name=str(raw.get("ipc_pipe_name", r"\\.\pipe\hubo_video_downloader")),
    )


WINDOWS_RESERVED_FILENAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def sanitize_filename_component(value: str, *, max_length: int = 80) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
    value = re.sub(r"\s+", " ", value).strip().strip(".")
    value = value[:max_length].rstrip(" .")

    if not value:
        return "video"

    if value.upper() in WINDOWS_RESERVED_FILENAMES:
        value = f"_{value}"

    return value


def detect_site(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]

    if host in {"youtube.com", "m.youtube.com", "youtu.be"} or host.endswith(".youtube.com"):
        return "youtube"
    if host in {"reddit.com", "www.reddit.com", "v.redd.it"} or host.endswith(".reddit.com"):
        return "reddit"
    if "redgifs.com" in host:
        return "redgif"
    if "pornhub.com" in host:
        return "pornhub"
    if "xvideos.com" in host:
        return "xvideo"
    if "streamtape.com" in host:
        return "streamtape"
    return "unknown"


def ensure_output_dir(config: WorkerConfig) -> Path:
    out_dir = config.default_output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def format_filename_timestamp(raw_timestamp: str) -> str:
    try:
        parsed = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
        return parsed.strftime("%Y%m%d_%H%M%S")
    except ValueError:
        return datetime.now().strftime("%Y%m%d_%H%M%S")


def build_output_template(job: DownloadJob, out_dir: Path) -> str:
    safe_title = sanitize_filename_component(job.page_title or "video", max_length=80)
    safe_timestamp = format_filename_timestamp(job.timestamp)
    return str(out_dir / f"{safe_timestamp}_{safe_title}-%(id)s.%(ext)s")


def run_yt_dlp_download(config: WorkerConfig, job: DownloadJob, url: str, site: str) -> tuple[int, str | None]:
    out_dir = ensure_output_dir(config)
    output_template = build_output_template(job, out_dir)

    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        url,
        "--no-playlist",
        "--restrict-filenames",
        "-o",
        output_template,
        "--print",
        "after_move:filepath",
    ]

    log_event("subprocess.start", requestId=job.request_id, stage=f"yt-dlp:{site}", command=cmd)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    log_event("subprocess.exit", requestId=job.request_id, stage=f"yt-dlp:{site}", returnCode=result.returncode)

    file_path: str | None = None
    for line in reversed((result.stdout or "").splitlines()):
        candidate = line.strip()
        if candidate and Path(candidate).exists():
            file_path = candidate
            break

    if result.returncode != 0 and result.stderr:
        log_event("subprocess.stderr", requestId=job.request_id, stage=f"yt-dlp:{site}", stderr=result.stderr[-1200:])

    return result.returncode, file_path


def open_file_in_explorer(file_path: Path) -> None:
    subprocess.Popen(["explorer.exe", "/select,", str(file_path)])


def notify_download_finished(file_path: Path) -> None:
    """Send Windows toast notification without using win10toast/win10toast_click.

    win10toast is known to fail on Python 3.11+ with:
    - "WNDPROC return value cannot be converted to LRESULT"
    - "TypeError: WPARAM is simple, so must be an int object (got NoneType)"
    (see upstream issue #112)
    """
    try:
        from win11toast import toast  # type: ignore[import-not-found]
    except Exception:  # pylint: disable=broad-except
        log_event(
            "notify.skipped",
            reason="toast_dependency_missing",
            message="Download succeeded, but desktop notification dependency is missing.",
            filePath=str(file_path),
        )
        return

    try:
        toast(
            "Hubo Video Downloader",
            f"Download finished: {file_path.name}",
            on_click=lambda _args: open_file_in_explorer(file_path),
        )
        log_event("notify.sent", backend="win11toast", filePath=str(file_path))
    except Exception as exc:  # pylint: disable=broad-except
        log_event("notify.failed", backend="win11toast", error=str(exc), filePath=str(file_path))


def run_streamtape_download(config: WorkerConfig, job: DownloadJob, repo_root: Path) -> tuple[int, str | None]:
    streamtape_cli = repo_root / "tools" / "streamtape_cli.py"
    if not streamtape_cli.exists():
        log_event("job.error", requestId=job.request_id, reason="streamtape_cli_missing", path=str(streamtape_cli))
        return 1, None

    extract_cmd = [sys.executable, str(streamtape_cli), job.url, "--quiet"]
    log_event("streamtape.extract.start", requestId=job.request_id, command=extract_cmd)
    extract = subprocess.run(extract_cmd, capture_output=True, text=True, check=False)
    if extract.returncode != 0:
        log_event(
            "streamtape.extract.failed",
            requestId=job.request_id,
            returnCode=extract.returncode,
            stderr=(extract.stderr or "").strip(),
        )
        return extract.returncode, None

    direct_url = (extract.stdout or "").strip()
    if not direct_url:
        log_event("streamtape.extract.failed", requestId=job.request_id, reason="empty_direct_url")
        return 1, None

    log_event("streamtape.extract.ok", requestId=job.request_id)
    return run_yt_dlp_download(config, job, direct_url, "streamtape")


def run_download_job(config: WorkerConfig, job: DownloadJob, repo_root: Path) -> None:
    site = detect_site(job.url)
    log_event("job.started", requestId=job.request_id, site=site, url=job.url)

    if site not in SUPPORTED_SITES:
        log_event("job.finished", requestId=job.request_id, site=site, status="unsupported")
        return

    try:
        if site == "streamtape":
            return_code, file_path = run_streamtape_download(config, job, repo_root)
        else:
            return_code, file_path = run_yt_dlp_download(config, job, job.url, site)

        if return_code == 0:
            log_event("job.finished", requestId=job.request_id, site=site, status="ok", filePath=file_path)
            if file_path:
                notify_download_finished(Path(file_path))
        else:
            log_event("job.finished", requestId=job.request_id, site=site, status="failed", returnCode=return_code)
    except Exception as exc:  # pylint: disable=broad-except
        log_event("job.crashed", requestId=job.request_id, site=site, error=str(exc))


class JobManager:
    def __init__(self, config: WorkerConfig, repo_root: Path) -> None:
        self._config = config
        self._repo_root = repo_root

    def enqueue(self, payload: dict[str, Any]) -> dict[str, Any]:
        for key in ("url", "pageHtml", "pageTitle", "timestamp"):
            if key not in payload or not isinstance(payload[key], str):
                raise ValueError(f"Invalid job field: {key}")

        site = detect_site(payload["url"])
        if site not in SUPPORTED_SITES:
            return {
                "ok": False,
                "status": "unsupported",
                "message": f"Unsupported URL/site: {payload['url']}",
            }

        request_id = str(uuid.uuid4())
        job = DownloadJob(
            request_id=request_id,
            url=payload["url"],
            page_html=payload["pageHtml"],
            page_title=payload["pageTitle"],
            timestamp=payload["timestamp"],
        )

        worker = threading.Thread(
            target=run_download_job,
            args=(self._config, job, self._repo_root),
            daemon=True,
            name=f"download-{request_id}",
        )
        worker.start()

        log_event("job.queued", requestId=request_id, site=site, url=job.url)
        return {
            "ok": True,
            "status": "queued",
            "message": "Download started.",
            "requestId": request_id,
            "site": site,
        }


def handle_connection(conn: Any, manager: JobManager) -> None:
    try:
        raw = conn.recv_bytes()
        message = json.loads(raw.decode("utf-8"))
        payload = message.get("job", message)
        response = manager.enqueue(payload)
    except Exception as exc:  # pylint: disable=broad-except
        response = {
            "ok": False,
            "status": "error",
            "message": f"Failed to queue job: {exc}",
        }

    conn.send_bytes(json.dumps(response, ensure_ascii=False).encode("utf-8"))
    conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hubo Video Downloader worker service")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[1] / "video_downloader.yaml"),
        help="Path to YAML config file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    repo_root = Path(__file__).resolve().parents[2]
    manager = JobManager(config, repo_root)

    log_event("worker.starting", configPath=str(config_path), pipeName=config.ipc_pipe_name)

    with Listener(address=config.ipc_pipe_name, family="AF_PIPE") as listener:
        log_event("worker.ready", pipeName=config.ipc_pipe_name)
        while True:
            conn = listener.accept()
            threading.Thread(target=handle_connection, args=(conn, manager), daemon=True).start()


if __name__ == "__main__":
    raise SystemExit(main())
