"""Agent 6 — SEO Editor.

Deterministic pass: validates and repairs slug, title lengths, meta
description, tags and category. No AI call needed — the writer already
produced SEO fields; this agent enforces the constraints.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .. import config, db
from ..art import ensure_art
from .base import traced


def _fix(draft: dict) -> tuple[dict, list[str]]:
    fixes: list[str] = []
    d = dict(draft)

    if not d.get("seoTitle"):
        d["seoTitle"] = d["headline"][:60]
        fixes.append("generated seoTitle")
    if len(d["seoTitle"]) > 65:
        d["seoTitle"] = d["seoTitle"][:62].rsplit(" ", 1)[0]
        fixes.append("shortened seoTitle")
    if not d.get("seoDescription"):
        d["seoDescription"] = (d.get("subheadline") or d["headline"])[:155]
        fixes.append("generated seoDescription")
    if "satire" not in d["seoDescription"].lower():
        d["seoDescription"] = ("Satire: " + d["seoDescription"])[:155]
        fixes.append("marked description as satire")
    if not isinstance(d.get("tags"), list) or not d["tags"]:
        d["tags"] = [w for w in re.findall(r"[a-z]{4,}", d["headline"].lower())][:4]
        fixes.append("generated tags")
    cats = {c["slug"] for c in json.loads(config.CATEGORIES_FILE.read_text())}
    if d.get("category") not in cats:
        d["category"] = "world-absurdities"
        fixes.append("category reset to world-absurdities")
    if not d.get("author"):
        d["author"] = "The Daily Absurd Staff"
        fixes.append("default author")
    d["art"] = ensure_art(d["slug"], d["category"], d["headline"], d.get("art"))
    return d, fixes


@traced("seo_editor")
def run() -> dict:
    drafts = db.query("SELECT * FROM drafts WHERE status='safety_ok'")
    done = 0
    for d in drafts:
        path = Path(d["path"])
        try:
            draft = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        fixed, fixes = _fix(draft)
        db.write_json(path, fixed)
        db.run(
            "INSERT INTO reviews (id, draft_id, reviewer, verdict, notes, created_at) VALUES (?,?,?,?,?,?)",
            (db.uid(), d["id"], "seo_editor", "pass",
             "; ".join(fixes) or "already compliant", db.now()),
        )
        db.run("UPDATE drafts SET status='approved', updated_at=? WHERE id=?",
               (db.now(), d["id"]))
        done += 1
    return {"detail": f"{done} drafts SEO-finalised", "approved": done}
