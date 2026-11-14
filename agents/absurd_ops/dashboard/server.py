"""Ops health dashboard — stdlib http.server, localhost only."""
from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .. import config, db

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Daily Absurd — Ops</title>
<meta http-equiv="refresh" content="30">
<style>
body{{font-family:Georgia,serif;background:#faf6ec;color:#16130e;max-width:1100px;margin:2rem auto;padding:0 1rem}}
h1{{border-bottom:4px solid #16130e;padding-bottom:.5rem}}
h2{{font-size:1.1rem;letter-spacing:.15em;text-transform:uppercase;border-top:3px solid #16130e;padding-top:.75rem;margin-top:2rem}}
table{{border-collapse:collapse;width:100%;font-size:.85rem;font-family:ui-monospace,monospace}}
td,th{{border:1px solid #ccc4b0;padding:.35rem .5rem;text-align:left;vertical-align:top}}
th{{background:#16130e;color:#faf6ec}}
.ok{{color:#137a2e}}.err{{color:#b92a08}}.run{{color:#b9920a}}
.kpis{{display:flex;flex-wrap:wrap;gap:1rem}}
.kpi{{border:2px solid #16130e;padding:.75rem 1.25rem;min-width:8rem}}
.kpi b{{display:block;font-size:1.9rem}}
.kpi span{{font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:#6f675a}}
a{{color:#e63b12}}
</style></head><body>
<h1>The Daily <i style="color:#e63b12">Absurd</i> — Ops Room</h1>
{body}
<p style="color:#6f675a;font-size:.75rem">auto-refresh 30s · {now}</p>
</body></html>"""


def esc(x) -> str:
    return html.escape(str(x if x is not None else ""))


def table(rows: list[dict], cols: list[str], raw: set[str] | None = None) -> str:
    if not rows:
        return "<p><i>none</i></p>"
    raw = raw or set()
    head = "".join(f"<th>{esc(c)}</th>" for c in cols)
    body = ""
    for r in rows:
        cells = "".join(
            f"<td>{r.get(c,'') if c in raw else esc(r.get(c,''))}</td>" for c in cols)
        body += f"<tr>{cells}</tr>"
    return f"<table><tr>{head}</tr>{body}</table>"


def render() -> str:
    db.init()
    counts = {
        "Trends": db.one("SELECT COUNT(*) n FROM trends")["n"],
        "Ideas": db.one("SELECT COUNT(*) n FROM story_ideas")["n"],
        "Drafts": db.one("SELECT COUNT(*) n FROM drafts")["n"],
        "Published": db.one("SELECT COUNT(*) n FROM published")["n"],
        "Subscribers": db.one("SELECT COUNT(*) n FROM subscribers WHERE status='subscribed'")["n"],
        "Failed runs (24h)": db.one(
            "SELECT COUNT(*) n FROM agent_runs WHERE status='error' AND started_at>datetime('now','-1 day')")["n"],
    }
    kpis = "".join(
        f'<div class="kpi"><b>{esc(v)}</b><span>{esc(k)}</span></div>' for k, v in counts.items())

    runs = db.query(
        "SELECT agent,status,substr(detail,1,120) detail,started_at,ended_at FROM agent_runs ORDER BY started_at DESC LIMIT 20")
    for r in runs:
        cls = {"ok": "ok", "error": "err"}.get(r["status"], "run")
        r["status"] = f'<span class="{cls}">{esc(r["status"])}</span>'

    drafts = db.query(
        "SELECT slug,status,comedy_score,safety_score,updated_at FROM drafts ORDER BY updated_at DESC LIMIT 15")
    pubs = db.query(
        "SELECT slug,url,deployed,published_at FROM published ORDER BY published_at DESC LIMIT 15")
    for p in pubs:
        p["url"] = f'<a href="{esc(p["url"])}">{esc(p["url"])}</a>'
    tasks = db.query(
        "SELECT kind,status,attempts,substr(last_error,1,80) last_error,updated_at FROM tasks WHERE status!='done' ORDER BY updated_at DESC LIMIT 10")
    metrics = db.query(
        "SELECT name,value,recorded_at FROM metrics ORDER BY recorded_at DESC LIMIT 20")

    body = f"""
<div class="kpis">{kpis}</div>
<h2>Agent runs</h2>{table(runs, ["agent","status","detail","started_at","ended_at"], {"status"})}
<h2>Draft queue</h2>{table(drafts, ["slug","status","comedy_score","safety_score","updated_at"])}
<h2>Published</h2>{table(pubs, ["slug","url","deployed","published_at"], {"url"})}
<h2>Open tasks</h2>{table(tasks, ["kind","status","attempts","last_error","updated_at"])}
<h2>Recent metrics</h2>{table(metrics, ["name","value","recorded_at"])}
"""
    return PAGE.format(body=body, now=db.now())


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/status"):
            payload = json.dumps(__import__("absurd_ops.pipeline", fromlist=["status"]).status())
            self._send(200, "application/json", payload)
            return
        self._send(200, "text/html; charset=utf-8", render())

    def _send(self, code, ctype, body):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


def serve() -> None:
    server = ThreadingHTTPServer((config.DASHBOARD_HOST, config.DASHBOARD_PORT), Handler)
    print(f"ops dashboard → http://{config.DASHBOARD_HOST}:{config.DASHBOARD_PORT}")
    server.serve_forever()
