from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from . import config, db, metrics, pipeline
from . import agents as A

AGENTS = {name: getattr(A, name) for name in A.__all__}


def _gsc_auth() -> int:
    """One-time OAuth consent for Search Console. Starts a loopback listener,
    opens the consent URL, exchanges the code for a refresh token, and prints
    the env vars to save."""
    client_id = config.GSC_CLIENT_ID or input("OAuth client ID: ").strip()
    secret = config.GSC_CLIENT_SECRET or input("OAuth client secret: ").strip()

    captured: dict[str, str] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            captured.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Auth received - you can close this tab.")

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), Handler)
    redirect = f"http://127.0.0.1:{srv.server_port}"
    url = ("https://accounts.google.com/o/oauth2/v2/auth?"
           + urllib.parse.urlencode({
               "client_id": client_id,
               "redirect_uri": redirect,
               "response_type": "code",
               "scope": metrics.GSC_SCOPE,
               "access_type": "offline",
               "prompt": "consent",
           }))
    print(f"Open this URL to authorise Search Console access:\n\n{url}\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    srv.handle_request()
    code = captured.get("code")
    if not code:
        print(f"no auth code received (got: {captured})", file=sys.stderr)
        return 1

    req = urllib.request.Request(metrics.GSC_TOKEN_URL, data=json.dumps({
        "client_id": client_id,
        "client_secret": secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect,
    }).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        tokens = json.loads(r.read().decode())
    refresh = tokens.get("refresh_token")
    if not refresh:
        print(f"no refresh_token in response: {tokens}", file=sys.stderr)
        return 1

    site = config.GSC_SITE_URL or input(
        "GSC property URL (e.g. https://daily-absurd.vercel.app/): ").strip()
    print("\nSave these in your environment (e.g. ~/.config/environment.d/ "
          "or a systemd drop-in):\n")
    print(f"ABSURD_GSC_SITE={site}")
    print(f"ABSURD_GSC_CLIENT_ID={client_id}")
    print(f"ABSURD_GSC_CLIENT_SECRET={secret}")
    print(f"ABSURD_GSC_REFRESH_TOKEN={refresh}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="absurd", description="Daily Absurd ops")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("daily")
    sub.add_parser("status")
    a = sub.add_parser("run-agent"); a.add_argument("name", choices=sorted(AGENTS))
    sub.add_parser("dashboard")
    sub.add_parser("metrics")
    sub.add_parser("gsc-auth")

    args = p.parse_args()
    db.init()

    if args.cmd == "init":
        print(f"db initialised at {db.config.DB_PATH}")
        return 0
    if args.cmd == "daily":
        print(json.dumps(pipeline.daily(), indent=2)[:8000])
        return 0
    if args.cmd == "status":
        print(json.dumps(pipeline.status(), indent=2))
        return 0
    if args.cmd == "run-agent":
        print(json.dumps(AGENTS[args.name](), indent=2))
        return 0
    if args.cmd == "dashboard":
        from .dashboard.server import serve
        serve()
        return 0
    if args.cmd == "metrics":
        print(json.dumps(metrics.collect(), indent=2))
        return 0
    if args.cmd == "gsc-auth":
        return _gsc_auth()
    return 1


if __name__ == "__main__":
    sys.exit(main())
