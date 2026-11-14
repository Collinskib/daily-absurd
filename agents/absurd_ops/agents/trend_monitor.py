"""Agent 1 — Global Trend Monitor.

Fetches international feeds, dedupes on source URL, and stores every item as
a trend candidate. Never treats an unverified post as established fact —
trends carry their source through the whole pipeline.
"""
from __future__ import annotations

from .. import db
from ..sources import fetch_trends
from .base import traced


@traced("trend_monitor")
def run() -> dict:
    items = fetch_trends()
    inserted = 0
    for it in items:
        exists = db.one("SELECT id FROM trends WHERE source_url=?", (it["url"],))
        if exists:
            continue
        db.run(
            """INSERT INTO trends (id, title, summary, source, source_url, region, fetched_at, raw_json)
               VALUES (?,?,?,?,?,?,?,?)""",
            (db.uid(), it["title"], it["summary"], it["source"], it["url"],
             it["region"], db.now(), "{}"),
        )
        inserted += 1
    return {"detail": f"{inserted} new trends (of {len(items)} fetched)", "inserted": inserted}
