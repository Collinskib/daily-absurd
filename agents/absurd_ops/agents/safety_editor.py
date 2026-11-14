"""Agent 5 — Factual Context & Safety Editor.

Two layers: deterministic pattern checks in Python (fake-alert markers,
real-name quote patterns, missing satire cues) and a Devin review that
verifies the underlying event is represented honestly and the satire is
distinguishable from news. Both must pass.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

from .. import config, db
from ..devin import run_session, read_json_output
from .base import traced

EMERGENCY_PATTERNS = [
    r"\bbreaking\s+(alert|news)\b", r"\bofficial\s+statement\b",
    r"\bemergency\s+(broadcast|alert)\b", r"\bevacuate\b", r"\bcivil\s+alert\b",
    r"\bamber alert\b", r"\bpublic\s+safety\s+(notice|announcement)\b",
]
SENSITIVE_PATTERNS = [
    r"\b(child|minor)s?\s+(abuse|assault)\b", r"\bschool\s+shooting\b",
    r"\bterroris[tm]\b", r"\bmass\s+grave\b", r"\bgenocide\b",
]


def _deterministic_check(draft: dict) -> list[str]:
    problems: list[str] = []
    body = draft.get("body", "")
    text = f"{draft.get('headline','')} {draft.get('subheadline','')} {body}"
    for p in EMERGENCY_PATTERNS:
        if re.search(p, text, re.I):
            problems.append(f"resembles emergency/official communication: /{p}/")
    for p in SENSITIVE_PATTERNS:
        if re.search(p, text, re.I):
            problems.append(f"touches sensitive topic: /{p}/")
    if not draft.get("sourceEvent"):
        problems.append("missing real-event attribution")
    if len(body.split()) < 200:
        problems.append("article too thin to establish parody framing")
    return problems


def _devin_safety_pass(draft: dict, out: Path) -> dict | None:
    prompt = config.BRIEFS_DIR / f"safety-{int(time.time())}-{draft['slug'][:30]}.md"
    prompt.write_text(f"""You are the FACTUAL CONTEXT & SAFETY EDITOR for The Daily
Absurd, a satirical publication. Verify this article:

REAL EVENT (what actually happened): {draft['sourceEvent']}
SOURCE: {draft.get('sourceUrl','')}

ARTICLE:
HEADLINE: {draft['headline']}
BODY:
{draft['body']}

Check:
1. The underlying real event is represented accurately in spirit (the fiction
   may exaggerate but must not invert what actually happened).
2. Fictional elements cannot reasonably be mistaken for factual reporting.
3. No invented quotes attributed to real identifiable people.
4. No fabricated allegations about real people (crime, corruption, illness…).
5. Nothing resembling an emergency alert or genuine official statement.
6. Satire targets institutions/absurdity — not victims or vulnerable groups.

Write JSON to {out}:
{{"verdict": "pass" | "fail", "score": 0-10,
  "problems": ["..."], "fix": "required fix or empty"}}
Write ONLY the JSON file.""")
    res = run_session(prompt, out, timeout=420)
    return read_json_output(out) if res.ok else None


@traced("safety_editor")
def run() -> dict:
    drafts = db.query("SELECT * FROM drafts WHERE status='comedy_ok'")
    checked = 0
    for d in drafts:
        draft = read_json_output(Path(d["path"]))
        if not draft:
            continue
        problems = _deterministic_check(draft)
        verdict = {"verdict": "fail", "score": 0, "problems": problems} if problems else None
        if verdict is None:
            out = config.REVIEWS_DIR / f"{d['slug']}-safety.json"
            verdict = _devin_safety_pass(draft, out) or {
                "verdict": "fail", "score": 0,
                "problems": ["safety review inconclusive — treated as fail"],
            }
        v = "fail" if problems else verdict.get("verdict", "fail")
        score = float(verdict.get("score", 0))
        notes = "; ".join(verdict.get("problems", problems) or [verdict.get("fix", "")])
        db.run(
            "INSERT INTO reviews (id, draft_id, reviewer, verdict, score, notes, created_at) VALUES (?,?,?,?,?,?,?)",
            (db.uid(), d["id"], "safety_editor", v, score, str(notes)[:1500], db.now()),
        )
        db.run(
            "UPDATE drafts SET safety_score=?, status=?, updated_at=? WHERE id=?",
            (score, "safety_ok" if v == "pass" else "safety_fail", db.now(), d["id"]),
        )
        checked += 1
    return {"detail": f"{checked} drafts safety-checked", "checked": checked}
