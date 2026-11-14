"""Agent 9 — Growth Analyst.

Aggregates local performance metrics (agent throughput, category mix,
subscriber file) into the metrics table and a weekly report. Real traffic
data comes from Vercel Analytics — the agent records what it can measure.
"""
from __future__ import annotations

import json

from .. import config, db
from .base import traced


@traced("growth_analyst")
def run() -> dict:
    stats = {
        "trends": db.one("SELECT COUNT(*) n FROM trends")["n"],
        "ideas": db.one("SELECT COUNT(*) n FROM story_ideas")["n"],
        "drafts": db.one("SELECT COUNT(*) n FROM drafts")["n"],
        "published": db.one("SELECT COUNT(*) n FROM published")["n"],
        "deployed": db.one("SELECT COUNT(*) n FROM published WHERE deployed=1")["n"],
        "failed_runs_24h": db.one(
            "SELECT COUNT(*) n FROM agent_runs WHERE status='error' AND started_at > datetime('now','-1 day')"
        )["n"],
    }
    subs_file = config.WEB_DIR / "content" / "subscribers.ndjson"
    subs = 0
    if subs_file.exists():
        subs = sum(1 for l in subs_file.read_text().splitlines()
                   if l.strip() and json.loads(l).get("status") == "subscribed")
    stats["subscribers"] = subs

    for name, value in stats.items():
        db.run(
            "INSERT INTO metrics (id, name, value, dims_json, recorded_at) VALUES (?,?,?,?,?)",
            (db.uid(), f"growth.{name}", float(value), "{}", db.now()),
        )

    # Category performance snapshot
    cats = db.query(
        """SELECT i.category, COUNT(*) n FROM published p
           JOIN drafts d ON d.id = p.draft_id
           JOIN story_ideas i ON i.id = d.idea_id
           GROUP BY 1"""
    ) or db.query("SELECT category, COUNT(*) n FROM drafts GROUP BY category")

    report_path = config.STATE_DIR / "growth-report.json"
    db.write_json(report_path, {"generated_at": db.now(), "stats": stats,
                                "by_category": cats})
    return {"detail": f"metrics recorded: {stats}", "stats": stats}
