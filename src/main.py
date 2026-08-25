"""Paste storage and the expiry cleanup daemon."""

import json
import os
import threading
import time
from pathlib import Path


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
