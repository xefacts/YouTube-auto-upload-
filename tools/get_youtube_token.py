#!/usr/bin/env python3
"""Create the YOUTUBE_TOKEN_JSON secret value (run this locally, never in CI).

The YouTube Data API cannot upload with a service account, so the pipeline
needs a user OAuth token. Google only issues that token after an interactive
consent screen, which is why this step runs on your own machine.

Usage
-----
1. Google Cloud Console -> APIs & Services -> Credentials ->
   "Create credentials" -> OAuth client ID -> Application type: Desktop app.
2. Download the client JSON (client_secret_*.json).
3. Install the helper dependency once:
       pip install google-auth-oauthlib
4. Run:
       python tools/get_youtube_token.py --client-secret path/to/client_secret_xxx.json
5. Copy the printed JSON into
   GitHub -> Settings -> Secrets and variables -> Actions -> YOUTUBE_TOKEN_JSON

The output looks like::

    {"client_id": "...", "client_secret": "...", "refresh_token": "...",
     "token_uri": "https://oauth2.googleapis.com/token",
     "scopes": ["https://www.googleapis.com/auth/youtube.upload"]}

Never commit the token JSON or the client secret to the repository.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mint a YOUTUBE_TOKEN_JSON value via OAuth consent")
    parser.add_argument("--client-secret", required=True, help="Desktop OAuth client JSON downloaded from Google Cloud")
    parser.add_argument("--out", help="Optional file to write the token JSON to")
    args = parser.parse_args(argv)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("google-auth-oauthlib is missing. Run: pip install google-auth-oauthlib", file=sys.stderr)
        return 2

    client_path = Path(args.client_secret)
    if not client_path.exists():
        print(f"{client_path} not found", file=sys.stderr)
        return 2
    client_config = json.loads(client_path.read_text())
    if "installed" not in client_config and "web" not in client_config:
        print(
            "That file is not an OAuth client JSON (expected an 'installed' or 'web' section). "
            "A service-account key cannot be used for YouTube uploads.",
            file=sys.stderr,
        )
        return 2

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)
    if not creds.refresh_token:
        print(
            "Google did not return a refresh_token. Revoke the app's access at "
            "https://myaccount.google.com/permissions and run this script again.",
            file=sys.stderr,
        )
        return 1

    section = client_config.get("installed") or client_config.get("web")
    token = {
        "client_id": section.get("client_id") or creds.client_id,
        "client_secret": section.get("client_secret") or creds.client_secret,
        "refresh_token": creds.refresh_token,
        "token_uri": section.get("token_uri") or creds.token_uri or "https://oauth2.googleapis.com/token",
        "scopes": SCOPES,
    }
    payload = json.dumps(token, indent=2)
    if args.out:
        Path(args.out).write_text(payload)
        print(f"Token written to {args.out}. Paste the whole JSON into the YOUTUBE_TOKEN_JSON secret.")
    else:
        print("\n=== Paste this JSON into the YOUTUBE_TOKEN_JSON secret ===\n")
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
