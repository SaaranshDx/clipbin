import sys
import argparse
import requests
from getpass import getpass

API_URL = "https://api.mizucode.qzz.io"
BASE_URL = "https://clipbin.github.io"

def main():
    parser = argparse.ArgumentParser(
        prog="clipbin",
        description="share text like never befour"
    )    
    parser.add_argument("--encrypt,", action="store_true")
    parser.add_argument("--duration,", type=int, default=168)

    args = parser.parse_args()
        