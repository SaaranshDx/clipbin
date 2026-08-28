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

def positive_duration(value):
    try:
        duration = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("duration must be a whole number") from error
    if duration <= 0:
        raise argparse.ArgumentTypeError("duration must be greater than zero")
    return duration


def main():
    parser = argparse.ArgumentParser(
        prog="clipbin",
        description="share text like never befour"
    )    
    parser.add_argument("--encrypt", action="store_true")
    parser.add_argument("--duration", type=positive_duration, default=168)

    args = parser.parse_args()
        
    if sys.stdin.isatty():
        parser.error("no input received; pipe text into clipbin")
        
    try:
        data = sys.stdin.read()
    except (OSError, UnicodeError) as error:
        parser.error(f"could not read input: {error}")
    
    if not data:
        parser.error("paste cannot be empty dummy!")
        
    if args.encrypt:
        try:
            key = getpass("Key: ")
            if not key:
                parser.error("encryption key cannot be empty")
            salt = os.urandom(16)
            iv = os.urandom(12)
            encryption_key = hashlib.pbkdf2_hmac(
                "sha256", key.encode("utf-8"), salt, 250_000, dklen=32
            )
            ciphertext = AESGCM(encryption_key).encrypt(
                iv, data.encode("utf-8"), None
            )
            data = json.dumps({
                "version": 1,
                "algorithm": "AES-GCM",
                "kdf": "PBKDF2-SHA-256",
                "iterations": 250000,
                "salt": base64.b64encode(salt).decode("ascii"),
                "iv": base64.b64encode(iv).decode("ascii"),
                "ciphertext": base64.b64encode(ciphertext).decode("ascii")
            }, separators=(",", ":"))
        except (EOFError, OSError, UnicodeError) as error:
            print(f"Error: could not encrypt paste: {error}", file=sys.stderr)
            return 1
        
    payload = {
        "data": data,
        "duration": args.duration
    }    
    
    try:
        response = requests.post(
            f"{API_URL}/pastes",
            json=payload,
            timeout=15
        )
    except requests.exceptions.RequestException as error:
        print(f"Error: could not reach API: {error}", file=sys.stderr)
        return 1
    
    if not response.ok:
        try:
            error = response.json().get("error", "unknown error")
        except (ValueError, AttributeError):
            error = response.text.strip() or "unknown error"
        print(f"Error: {error}", file=sys.stderr)
        return 1
        
    try:
        paste_id = response.json()["id"]
        if not isinstance(paste_id, str) or not paste_id:
            raise ValueError
    except (ValueError, KeyError, TypeError):
        print("Error: API returned an invalid response", file=sys.stderr)
        return 1
    print(f"{BASE_URL}/{paste_id}")                    
    return 0
    
if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nError: cancelled", file=sys.stderr)
        sys.exit(130)
