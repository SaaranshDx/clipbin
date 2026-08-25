"""Paste storage and the expiry cleanup daemon."""

import json
import os
import threading
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PASTES_PATH = Path(os.getenv("PISTA_PASTES_PATH", PROJECT_ROOT / "db"))
PASTES_META_PATH = PASTES_PATH / "meta"
SECONDS_PER_HOUR = 60 * 60


def write_metadata(id, duration):
    """Store the paste's expiry information. ``duration`` is in hours."""
    try:
        if duration < 0:
            return False
        PASTES_META_PATH.mkdir(parents=True, exist_ok=True)
        metadata = {"id": id, "duration": duration, "created_at": time.time()}
        with (PASTES_META_PATH / f"{id}.json").open("x", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)
        return True
    except (FileExistsError, OSError, TypeError, ValueError):
        return False


def create_paste(id, data):
    try:
        PASTES_PATH.mkdir(parents=True, exist_ok=True)
        with (PASTES_PATH / f"{id}.txt").open("w", encoding="utf-8") as file:
            file.write(data)
        return True
    except (OSError, TypeError, ValueError):
        return False


def read_paste(id):
    try:
        return (PASTES_PATH / f"{id}.txt").open(encoding="utf-8")
    except OSError:
        return False


def cleanup_expired_pastes(now=None, pastes_path=None, metadata_path=None):
    """Delete expired paste files and their metadata, returning the count."""
    paste_dir = Path(pastes_path or PASTES_PATH)
    meta_dir = Path(metadata_path or PASTES_META_PATH)
    current_time = time.time() if now is None else now
    removed = 0
    if not meta_dir.exists():
        return removed

    for metadata_file in meta_dir.glob("*.json"):
        try:
            with metadata_file.open(encoding="utf-8") as file:
                metadata = json.load(file)
            paste_id = metadata["id"]
            created_at = float(metadata["created_at"])
            duration = float(metadata["duration"])
            paste_name = Path(str(paste_id)).name
            if paste_name != str(paste_id) or duration < 0:
                continue
            if current_time < created_at + duration * SECONDS_PER_HOUR:
                continue

            paste_file = paste_dir / f"{paste_name}.txt"
            if paste_file.exists():
                paste_file.unlink()
            metadata_file.unlink()
            removed += 1
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            continue
    return removed


def cleanup_daemon(interval=60, stop_event=None):
    """Run cleanup periodically until ``stop_event`` is set."""
    if interval <= 0:
        raise ValueError("interval must be greater than zero")
    stop_event = stop_event or threading.Event()
    while not stop_event.is_set():
        cleanup_expired_pastes()
        stop_event.wait(interval)


def start_cleanup_daemon(interval=60):
    """Start the cleanup daemon and return ``(thread, stop_event)``."""
    stop_event = threading.Event()
    thread = threading.Thread(
        target=cleanup_daemon,
        args=(interval, stop_event),
        name="pista-paste-cleanup",
        daemon=True,
    )
    thread.start()
    return thread, stop_event


class PasteRequestHandler(BaseHTTPRequestHandler):
    """HTTP routes for creating and viewing pastes."""

    server_version = "Pista/1.0"

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _paste_id(self, path):
        prefix = "/pastes/"
        if not path.startswith(prefix):
            return None
        paste_id = unquote(path[len(prefix):])
        if not paste_id or "/" in paste_id or "\\" in paste_id or paste_id in {".", ".."}:
            return None
        return paste_id

    def do_POST(self):
        if urlsplit(self.path).path != "/pastes":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "route not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 1_048_576:
                raise ValueError("request body must be between 1 byte and 1 MiB")
            payload = json.loads(self.rfile.read(content_length))
            data = payload["data"]
            duration = float(payload["duration"])
            paste_id = payload.get("id") or uuid.uuid4().hex
            if not isinstance(data, str) or not data:
                raise ValueError("data must be a non-empty string")
            if not duration >= 0 or not isinstance(paste_id, str):
                raise ValueError("duration or id is invalid")
            if Path(paste_id).name != paste_id:
                raise ValueError("id must be a filename-safe value")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "expected data and duration"})
            return

        if not create_paste(paste_id, data) or not write_metadata(paste_id, duration):
            self._send_json(HTTPStatus.CONFLICT, {"error": "paste id already exists"})
            return
        self._send_json(HTTPStatus.CREATED, {"id": paste_id})

    def do_GET(self):
        paste_id = self._paste_id(urlsplit(self.path).path)
        if paste_id is None:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "route not found"})
            return
        paste = read_paste(paste_id)
        if paste is False:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "paste not found"})
            return
        with paste:
            self._send_json(HTTPStatus.OK, {"id": paste_id, "data": paste.read()})

    def log_message(self, format, *args):
        return


def run_server(host="127.0.0.1", port=8000, cleanup_interval=60):
    """Run the HTTP server and cleanup daemon until interrupted."""
    cleanup_thread, stop_event = start_cleanup_daemon(cleanup_interval)
    server = ThreadingHTTPServer((host, port), PasteRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        cleanup_thread.join(timeout=2)
        server.server_close()


if __name__ == "__main__":
    run_server()
