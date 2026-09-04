"""Routes for the envy API namespace.

The module is intentionally kept as a separate router so routes can be added
without changing the application setup in ``main.py``.
"""

from fastapi import APIRouter
import secrets
import hashlib
import base64

raw = secrets.token_bytes(256)

s = base64.urlsafe_b64encode(
    hashlib.sha512(raw).digest() +
    hashlib.sha3_512(raw).digest()
).decode()

def get_pool_init_token():
    s = base64.urlsafe_b64encode(
    hashlib.sha512(raw).digest() +
    hashlib.sha3_512(raw).digest()
    ).decode()
    return s

router = APIRouter()

@router.get("/pool/init")
def init_pool():
    pool_init_token = get_pool_init_token()
    return {"setupurl": f"https://clipbin.github.io/setup/?token={pool_init_token}"}