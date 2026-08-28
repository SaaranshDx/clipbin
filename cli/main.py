import sys
import argparse
import base64
import binascii
import hashlib
import json
import os
from urllib.parse import urlparse
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from getpass import getpass

API_URL = "https://api.ghostdrop.qzz.io"
BASE_URL = "https://clipbin.github.io"


def paste_endpoint(reference, parser):
    if reference.startswith(("http://", "https://")):
        path = urlparse(reference).path.rstrip("/")
        paste_id = path.rsplit("/", 1)[-1] if path else ""
    else:
        paste_id = reference

    if not paste_id or paste_id in (".", "..") or "/" in paste_id or "\\" in paste_id:
        parser.error("paste must be an ID or a paste URL")
    return f"{API_URL}/pastes/{paste_id}"


def get_paste(reference, parser):
    try:
        response = requests.get(
            paste_endpoint(reference, parser), timeout=15, allow_redirects=True
        )
    except requests.exceptions.RequestException as error:
        print(f"Error: could not reach API: {error}", file=sys.stderr)
        return 1

    if not response.ok:
        try:
            error = response.json().get("error", "paste not found or expired")
        except (ValueError, AttributeError):
            error = response.text.strip() or "paste not found or expired"
        print(f"Error: {error}", file=sys.stderr)
        return None

    return response.text


def decrypt_paste(payload, passphrase):
    encrypted = json.loads(payload)
    if (
        encrypted.get("version") != 1
        or encrypted.get("algorithm") != "AES-GCM"
        or encrypted.get("kdf") != "PBKDF2-SHA-256"
        or encrypted.get("iterations") != 250000
    ):
        raise ValueError("unsupported encrypted paste")

    salt = base64.b64decode(encrypted["salt"], validate=True)
    iv = base64.b64decode(encrypted["iv"], validate=True)
    ciphertext = base64.b64decode(encrypted["ciphertext"], validate=True)
    if len(salt) != 16 or len(iv) != 12:
        raise ValueError("invalid encrypted paste")
    encryption_key = hashlib.pbkdf2_hmac(
        "sha256", passphrase.encode("utf-8"), salt, 250000, dklen=32
    )
    plaintext = AESGCM(encryption_key).decrypt(iv, ciphertext, None)
    return plaintext.decode("utf-8")

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
    parser.add_argument("command", nargs="?")
    parser.add_argument("reference", nargs="?")
    parser.add_argument("--encrypt", action="store_true")
    parser.add_argument("--decrypt", action="store_true")
    parser.add_argument("--duration", type=positive_duration, default=168)

    args = parser.parse_args()

    if args.command == "get":
        if not args.reference:
            parser.error("get requires a paste ID or URL")
        if args.encrypt:
            parser.error("--encrypt cannot be used with get")
        data = get_paste(args.reference, parser)
        if data is None:
            return 1
        if args.decrypt:
            try:
                key = getpass("Key: ")
                if not key:
                    parser.error("decryption key cannot be empty")
                data = decrypt_paste(data, key)
            except (EOFError, OSError, UnicodeError) as error:
                print(f"Error: could not decrypt paste: {error}", file=sys.stderr)
                return 1
            except (AttributeError, InvalidTag, KeyError, TypeError, ValueError, binascii.Error):
                print("Error: invalid key or encrypted paste", file=sys.stderr)
                return 1
        sys.stdout.write(data)
        return 0
    if args.command is not None:
        parser.error(f"unknown command: {args.command}")
    if args.reference is not None or args.decrypt:
        parser.error("--decrypt and positional arguments are only valid with get")
        
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
