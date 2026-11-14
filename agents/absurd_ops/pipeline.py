"""Daily editorial pipeline — the autonomous newsroom loop."""
from __future__ import annotations

import json
import time

from . import config, db
from .agents import (
    trend_monitor, opportunity_analyst, writer, comedy_editor,
    safety_editor, seo_editor, social_agent, publishing_agent,
    growth_analyst, revenue_strategist,
)


def sync_subscribers() -> int:
    """Ingest the GitHub-committed subscribers.ndjson into the DB."""
    f = config.WEB_DIR / "content" / "subscribers.ndjson"
    if not f.exists():
        return 0
    n = 0
    for line in f.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        email = rec.get("email", "").lower()
        if not email:
            continue
        db.run(
            """INSERT INTO subscribers (email, status, updated_at) VALUES (?,?,?)
               ON CONFLICT(email) DO UPDATE SET status=excluded.status, updated_at=excluded.updated_at""",
            (email, rec.get("status", "subscribed"), rec.get("at", db.now())),
        )
        n += 1
    return n


def daily() -> dict:
    """The whole newsroom, once. Safe to re-run — every stage is idempotent."""
    db.init()
    t0 = time.time()
    results: dict[str, dict] = {}

    results["subscribers"] = {"synced": sync_subscribers()}
    results["trend_monitor"] = trend_monitor()
    results["opportunity_analyst"] = opportunity_analyst()
    results["writer"] = writer()
    results["comedy_editor"] = comedy_editor()
    results["safety_editor"] = safety_editor()
    results["seo_editor"] = seo_editor()
    results["social_agent"] = social_agent()
    results["publishing_agent"] = publishing_agent()
    results["growth_analyst"] = growth_analyst()
    results["revenue_strategist"] = revenue_strategist()

    results["_elapsed_seconds"] = round(time.time() - t0, 1)
    out = config.STATE_DIR / "last-run.json"
    db.write_json(out, results)
    return results


def status() -> dict:
    db.init()
    return {
        "trends": db.one("SELECT COUNT(*) n FROM trends"),
        "ideas_by_status": db.query("SELECT status, COUNT(*) n FROM story_ideas GROUP BY status"),
        "drafts_by_status": db.query("SELECT status, COUNT(*) n FROM drafts GROUP BY status"),
        "published": db.query("SELECT slug, url, deployed, published_at FROM published ORDER BY published_at DESC LIMIT 10"),
        "recent_runs": db.query("SELECT agent, status, detail, started_at, ended_at FROM agent_runs ORDER BY started_at DESC LIMIT 15"),
        "subscribers": db.one("SELECT COUNT(*) n FROM subscribers WHERE status='subscribed'"),
    }
