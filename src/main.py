
import json
import html
import os
import threading
import time
from pathlib import Path
import random
import string
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
import uvicorn
from fastapi.responses import HTMLResponse

PROJECT_ROOT = Path(__file__).resolve().parent
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


def is_encrypted_payload(data):
    try:
        payload = json.loads(data)
        return isinstance(payload, dict) and (
            payload.get("version") == 1
            and payload.get("algorithm") == "AES-GCM"
            and payload.get("kdf") == "PBKDF2-SHA-256"
        )
    except (TypeError, ValueError, json.JSONDecodeError):
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
        name="clipbin-paste-cleanup",
        daemon=True,
    )
    thread.start()
    return thread, stop_event


app = FastAPI(title="clipbin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Paste-Encrypted"],
)


class PasteCreateRequest(BaseModel):
    data: str
    duration: float
    id: str | None = None

@app.get("/", response_class=HTMLResponse)
def root():
    index_path = Path(__file__).resolve().parent / "public" / "index.html"
    try:
        with index_path.open(encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    except OSError:
        raise HTTPException(status_code=500, detail="looks like smth is fucked")    

@app.get("/api", response_class=HTMLResponse)
def api_docs():
    api_path = Path(__file__).resolve().parent / "public" / "api.html"
    try:
        with api_path.open(encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    except OSError:
        raise HTTPException(status_code=500, detail="api documentation not found")

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
        data = paste.read()
    return Response(
        content=data,
        media_type="text/plain",
        headers={"X-Paste-Encrypted": str(is_encrypted_payload(data)).lower()},
    )

@app.get("/styles", response_class=Response)
def styles():
    styles_path = Path(__file__).resolve().parent / "public" / "style.css"
    try:
        with styles_path.open(encoding="utf-8") as file:
            return Response(content=file.read(), media_type="text/css")
    except OSError:
        raise HTTPException(status_code=404, detail="styles not found")

@app.get("/index", response_class=Response)
def index_js():
    index_js_path = Path(__file__).resolve().parent / "public" / "index.js"
    try:
        with index_js_path.open(encoding="utf-8") as file:
            return Response(content=file.read(), media_type="application/javascript")
    except OSError:
        raise HTTPException(status_code=404, detail="index.js not found")

@app.get("/crypto", response_class=Response)
def crypto_js():
    crypto_js_path = Path(__file__).resolve().parent / "public" / "crypto.js"
    try:
        with crypto_js_path.open(encoding="utf-8") as file:
            return Response(content=file.read(), media_type="application/javascript")
    except OSError:
        raise HTTPException(status_code=404, detail="crypto.js not found")

@app.get("/{pasteid}", response_class=HTMLResponse)
def show_raw_paste(pasteid):
    if Path(pasteid).name != pasteid:
        raise HTTPException(status_code=404, detail="paste not found")

    paste = read_paste(pasteid)
    if paste is False:
        raise HTTPException(status_code=404, detail="paste not found")
    paste.close()

    paste_content_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>clipbin - {pasteid}</title>
    <link rel="stylesheet" href="/styles">
    </head>
    <body>
    <div class="app">
    <header>
    <h1>{pasteid}</h1>
    <span id="paste-status" class="paste-status">loading</span>
    <button id="copy-button" onclick="copyPaste()" disabled>copy</button>
    </header>
    <main class="paste-content">
    <pre id="paste-content">loading paste...</pre>
    </main>
    </div>
    <div class="modal-overlay" id="decryption-modal" onclick="if(event.target===this)cancelDecryption()">
      <div class="modal key-modal">
        <div class="modal-header">
          <h2>Decrypt paste</h2>
          <button class="modal-close" onclick="cancelDecryption()">&times;</button>
        </div>
        <div class="modal-body">
          <p class="modal-desc">Enter the key used when this paste was created.</p>
          <input id="decryption-key" class="modal-input" type="password" placeholder="encryption key" autocomplete="current-password">
          <p id="decryption-error" class="modal-desc" hidden>wrong key</p>
          <div class="modal-actions">
            <button class="button-secondary" onclick="cancelDecryption()">cancel</button>
            <button onclick="confirmDecryption()">decrypt</button>
          </div>
        </div>
      </div>
    </div>
    <script src="/crypto"></script>
    <script>
    let decryptionKeyResolver = null;

    function requestDecryptionKey() {{
        const modal = document.getElementById('decryption-modal');
        const input = document.getElementById('decryption-key');
        document.getElementById('decryption-error').hidden = true;
        input.value = '';
        modal.classList.add('open');
        setTimeout(() => input.focus(), 0);
        return new Promise((resolve) => {{ decryptionKeyResolver = resolve; }});
    }}

    function closeDecryptionModal() {{
        document.getElementById('decryption-modal').classList.remove('open');
        decryptionKeyResolver = null;
    }}

    function confirmDecryption() {{
        const key = document.getElementById('decryption-key').value;
        if (!key) return;
        if (decryptionKeyResolver) decryptionKeyResolver(key);
        closeDecryptionModal();
    }}

    function cancelDecryption() {{
        if (decryptionKeyResolver) decryptionKeyResolver(null);
        closeDecryptionModal();
    }}

    async function loadPaste() {{
        const content = document.getElementById('paste-content');
        try {{
            const pasteId = window.location.pathname.split('/').filter(Boolean).pop();
            const response = await fetch(`/pastes/${{encodeURIComponent(pasteId)}}`);
            if (!response.ok) {{
                throw new Error('paste not found or expired');
            }}
            const payload = await response.text();
            const encrypted = response.headers.get('X-Paste-Encrypted') === 'true' || isEncryptedPaste(payload);
            document.getElementById('paste-status').textContent = encrypted ? 'encrypted' : 'plain text';
            if (!encrypted) {{
                content.textContent = payload;
                document.getElementById('copy-button').disabled = false;
                return;
            }}

            const key = await requestDecryptionKey();
            if (!key) {{
                content.textContent = 'decryption cancelled';
                return;
            }}
            const plaintext = await decryptPaste(payload, key);
            content.textContent = plaintext;
            document.getElementById('copy-button').disabled = false;
        }} catch (error) {{
            document.getElementById('decryption-error').hidden = false;
            content.textContent = 'wrong key or corrupted paste';
        }}
    }}

    function copyPaste() {{
        const text = document.querySelector('pre').textContent;
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.querySelector('header button');
            btn.textContent = 'copied';
            setTimeout(() => {{ btn.textContent = 'copy'; }}, 2000);
        }});
    }}

    loadPaste();
    </script>
    </body>
    </html>
    """
    return paste_content_html.format(
        pasteid=html.escape(pasteid),
    )
    


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
