"""Agent 9 — Growth Analyst.

Aggregates local performance metrics (agent throughput, category mix,
subscriber file) into the metrics table and a weekly report. Traffic
comes from Vercel Web Analytics + Google Search Console via metrics.py —
each source degrades to an error note, never a failed run.
"""
from __future__ import annotations

import json

from .. import config, db, metrics
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

    traffic = metrics.collect()
    target = traffic.get("target", {})
    flat = {
        "vercel_visitors_mtd": target.get("visitors_mtd", 0),
        "vercel_pageviews_mtd": (traffic.get("vercel") or {}).get("pageviews", 0),
        "gsc_clicks_28d": (traffic.get("search_console") or {}).get("clicks_28d", 0),
        "gsc_impressions_28d": (traffic.get("search_console") or {}).get("impressions_28d", 0),
        "target_pct": target.get("pct_of_target", 0),
    }
    for name, value in {**stats, **flat}.items():
        prefix = "growth" if name in stats else "traffic"
        db.run(
            "INSERT INTO metrics (id, name, value, dims_json, recorded_at) VALUES (?,?,?,?,?)",
            (db.uid(), f"{prefix}.{name}", float(value or 0), "{}", db.now()),
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
                                "by_category": cats, "traffic": traffic})
    pace = (f"readers {target.get('visitors_mtd', 0)}/{target.get('monthly_readers', 0)} "
            f"({target.get('pct_of_target', 0)}%)")
    return {"detail": f"metrics recorded: {stats} | {pace}",
            "stats": stats, "traffic": traffic}
