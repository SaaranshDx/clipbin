
import json
import os
import threading
import time
from pathlib import Path
import random
import string
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
import uvicorn


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PASTES_PATH = Path(os.getenv("PISTA_PASTES_PATH", PROJECT_ROOT / "db"))
PASTES_META_PATH = PASTES_PATH / "meta"
SECONDS_PER_HOUR = 60 * 60


def write_metadata(id, duration):

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
    if interval <= 0:
        raise ValueError("interval must be greater than zero")
    stop_event = stop_event or threading.Event()
    while not stop_event.is_set():
        cleanup_expired_pastes()
        stop_event.wait(interval)


def start_cleanup_daemon(interval=60):
    stop_event = threading.Event()
    thread = threading.Thread(
        target=cleanup_daemon,
        args=(interval, stop_event),
        name="pista-paste-cleanup",
        daemon=True,
    )
    thread.start()
    return thread, stop_event


app = FastAPI(title="Pista")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PasteCreateRequest(BaseModel):
    data: str
    duration: float
    id: str | None = None


@app.post("/pastes", status_code=201)
def create_paste_route(payload: PasteCreateRequest):
    data = payload.data
    duration = payload.duration
    paste_id = payload.id or ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    valid_id = Path(paste_id).name == paste_id
    if not data or not valid_id:
        raise HTTPException(status_code=400, detail="invalid paste data or id")
    if not duration:
        duration = 168

    if not create_paste(paste_id, data) or not write_metadata(paste_id, duration):
        raise HTTPException(status_code=409, detail="paste id already exists")
    return {"id": paste_id}


@app.get("/pastes/{paste_id}")
def view_paste_route(paste_id):
    if Path(paste_id).name != paste_id:
        raise HTTPException(status_code=404, detail="paste not found")
    paste = read_paste(paste_id)
    if paste is False:
        raise HTTPException(status_code=404, detail="paste not found")
    with paste:
        return paste.read()


def run_server(host="127.0.0.1", port=8000, cleanup_interval=60):
    cleanup_thread, stop_event = start_cleanup_daemon(cleanup_interval)
    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        cleanup_thread.join(timeout=2)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not found File must have expired dummy!"
            }
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail
        }
    )

if __name__ == "__main__":
    run_server()
