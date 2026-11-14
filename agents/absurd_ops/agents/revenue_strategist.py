"""Agent 10 — Revenue Strategist.

Maintains the monetization readiness ledger in the DB: what infrastructure
exists, what needs approval, what is blocked. Never activates paid services
— this agent only tracks readiness.
"""
from __future__ import annotations

from .. import db
from .base import traced

STREAMS = [
    ("display_ads", "Layout has dedicated ad slots marked data-ad; network application pending site traffic + approval"),
    ("newsletter_sponsorship", "Subscriber pipeline live; rate card drafted; needs ESP + list size threshold"),
    ("premium_membership", "Paywall hooks designed; needs payment provider approval"),
    ("merchandise", "Share-card designs reusable as merch art; needs print partner"),
    ("affiliate", "Disclosure framework in editorial policy; needs partner programs"),
    ("licensing", "Original corpus accumulating; needs syndication contacts"),
]


@traced("revenue_strategist")
def run() -> dict:
    for name, note in STREAMS:
        db.run(
            "INSERT INTO metrics (id, name, value, dims_json, recorded_at) VALUES (?,?,?,?,?)",
            (db.uid(), f"monetization.{name}", 0.0,
             f'{{"status": "prepared-not-active", "note": {note!r}}}'.replace("'", '"'),
             db.now()),
        )
    return {"detail": f"{len(STREAMS)} revenue streams tracked (none active)", "streams": len(STREAMS)}
