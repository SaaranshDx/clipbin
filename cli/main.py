import sys
import argparse
import requests
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
        #encryption will be implimented here
        
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