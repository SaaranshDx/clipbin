import sys
import argparse
import base64
import hashlib
import json
import os
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from getpass import getpass

API_URL = "https://api.ghostdrop.qzz.io"
BASE_URL = "https://clipbin.github.io"

def main():
    parser = argparse.ArgumentParser(
        prog="clipbin",
        description="share text like never befour"
    )    
    parser.add_argument("--encrypt", action="store_true")
    parser.add_argument("--duration", type=int, default=168)

    args = parser.parse_args()
        
    if sys.stdin.isatty():
        print("Nothing to paste")
        
    data = sys.stdin.read()
    
    if not data:
        parser.error("paste cannot be empty dummy!")
        
    if args.encrypt:
        key = getpass("Key:")
        salt = os.urandom(16)
        iv = os.urandom(12)
        encryption_key = hashlib.pbkdf2_hmac(
            "sha256", key.encode("utf-8"), salt, 250_000, dklen=32
        )
        ciphertext = AESGCM(encryption_key).encrypt(iv, data.encode("utf-8"), None)
        data = json.dumps({
            "version": 1,
            "algorithm": "AES-GCM",
            "kdf": "PBKDF2-SHA-256",
            "iterations": 250000,
            "salt": base64.b64encode(salt).decode("ascii"),
            "iv": base64.b64encode(iv).decode("ascii"),
            "ciphertext": base64.b64encode(ciphertext).decode("ascii")
        }, separators=(",", ":"))
        
    payload = {
        "data": data,
        "duration": args.duration
    }    
    
    response = requests.post(
        f"{API_URL}/pastes",
        json=payload,
        timeout=15
    )
    
    if not response.ok:
        try:
            error = requests.json().get("error", "unknown error")
        except Exception:
            error = response.text
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
        
    paste_id = response.json()["id"]
    print(f"{BASE_URL}/{paste_id}")                    
    
if __name__ == "__main__":
    main()
